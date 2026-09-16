"""Integration tests using real Ansible and an offline rclone alias remote."""

import json
import os
from pathlib import Path
import pwd
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


class StorageRoleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="booksync-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "library" / "Books").mkdir(parents=True)
        (self.root / "library" / "Books" / "example.epub").write_text("fixture")
        self.config = self.root / "rclone.conf"
        self.original = (
            f"[books]\ntype = alias\nremote = {self.root}/library\n"
            "[unrelated]\ntype = local\n"
        )
        self.config.write_text(self.original)
        self.config.chmod(0o600)
        self.playbook = self.root / "play.yml"
        self.playbook.write_text(json.dumps([{
            "name": "Exercise storage role", "hosts": "localhost",
            "gather_facts": True, "roles": ["books_rclone"],
        }]))
        self.variables = {
            "books_rclone_user": pwd.getpwuid(os.getuid()).pw_name,
            "books_rclone_group": str(os.getgid()),
            "books_rclone_config": str(self.config),
            "books_rclone_local_directories": [str(self.root / "state")],
        }

    def run_role(self, overrides=None, check=False, success=True):
        variables = self.variables | (overrides or {})
        varfile = self.root / "vars.json"
        varfile.write_text(json.dumps(variables))
        env = os.environ | {
            "ANSIBLE_CONFIG": str(REPO / "ansible.cfg"),
            "ANSIBLE_ROLES_PATH": str(REPO / "roles"),
            "ANSIBLE_NOCOLOR": "1",
            "RCLONE_CONFIG": str(self.config),
        }
        command = ["ansible-playbook", "-i", "localhost,", "-c", "local",
                   str(self.playbook), "-e", f"@{varfile}"]
        if check:
            command.append("--check")
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode == 0, success, output)
        if self.config.exists():
            self.assertEqual(self.config.read_text(), self.original)
        return output

    def test_converges_and_is_idempotent(self):
        self.run_role()
        self.assertTrue((self.root / "state").is_dir())
        self.assertEqual((self.root / "state").stat().st_mode & 0o777, 0o750)
        self.assertRegex(self.run_role(), r"changed=0\s")
        self.assertRegex(self.run_role(check=True), r"changed=0\s")

    def test_discovers_active_config(self):
        self.run_role({"books_rclone_config": ""})

    def test_empty_root_directory_is_valid(self):
        (self.root / "library" / "Books" / "example.epub").unlink()
        self.run_role()

    def test_check_mode_validates_without_creating_directories(self):
        self.run_role(check=True)
        self.assertFalse((self.root / "state").exists())

    def test_failure_cases_do_not_create_directories(self):
        cases = [
            ({"books_rclone_binary": "/missing/rclone"}, "Install rclone first"),
            ({"books_rclone_config": str(self.root / "missing.conf")}, "missing or unreadable"),
            ({"books_rclone_remote": "absent"}, "remote is missing"),
            ({"books_rclone_root": "absent"}, "Books root is inaccessible"),
            ({"books_rclone_remote": "books:"}, "remote name without a colon"),
            ({"books_rclone_root": "../outside"}, "relative books root"),
        ]
        for variables, message in cases:
            with self.subTest(variables=variables):
                output = self.run_role(variables, success=False)
                self.assertIn(message, output)
                self.assertFalse((self.root / "state").exists())


if __name__ == "__main__":
    unittest.main()
