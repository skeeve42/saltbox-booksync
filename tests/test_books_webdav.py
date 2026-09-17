"""Deploy real systemd/rclone and exercise WebDAV without cloud credentials."""

import base64
import json
import os
from pathlib import Path
import pwd
import socket
import subprocess
import tempfile
import unittest
import urllib.error
import urllib.request
import uuid

import yaml

import test_books_rclone


class WebdavRoleTests(unittest.TestCase):
    run_role = test_books_rclone.StorageRoleTests.run_role

    def setUp(self):
        # PrivateTmp in the deployed unit intentionally hides /tmp and /var/tmp.
        self.root = Path(tempfile.mkdtemp(prefix="booksync-webdav-", dir=Path.home()))
        self.addCleanup(self.cleanup)
        self.service = "books-webdav-test-" + uuid.uuid4().hex[:8]
        self.unit = Path("/etc/systemd/system") / (self.service + ".service")
        self.ebooks = self.root / "library" / "Books" / "Ebooks"
        self.ebooks.mkdir(parents=True)
        (self.ebooks / "A book.epub").write_bytes(b"EPUB fixture content")
        (self.ebooks.parent / "private-audiobook.mp3").write_bytes(b"private")
        self.config = self.root / "rclone.conf"
        self.original = f"[books]\ntype = alias\nremote = {self.root}/library\n[other]\ntype = local\n"
        self.config.write_text(self.original)
        self.config.chmod(0o600)
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            self.port = listener.getsockname()[1]
        self.variables = {
            "books_rclone_user": pwd.getpwuid(os.getuid()).pw_name,
            "books_rclone_group": str(os.getgid()),
            "books_rclone_config": str(self.config),
            "books_rclone_local_directories": [str(self.root / "storage-state")],
            "books_webdav_state_path": str(self.root / "service-state"),
            "books_webdav_service_name": self.service,
            "books_webdav_port": self.port,
            "books_webdav_traefik_enabled": False,
            "books_webdav_username": "reader",
            "books_webdav_password": 'test-only-$%\\" strong password',
        }
        self.playbook = self.root / "play.yml"
        self.playbook.write_text(json.dumps([{
            "name": "Exercise WebDAV role", "hosts": "localhost",
            "gather_facts": True, "roles": ["books_webdav"],
        }]))
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def cleanup(self):
        prefix = [] if os.getuid() == 0 else ["sudo", "-n"]
        subprocess.run(prefix + ["systemctl", "disable", "--now", self.service],
                       capture_output=True, check=False)
        subprocess.run(prefix + ["rm", "-f", str(self.unit)], check=True)
        subprocess.run(prefix + ["systemctl", "daemon-reload"], check=True)
        subprocess.run(prefix + ["rm", "-rf", str(self.root)], check=True)

    def request(self, path="/", method="GET", auth=True, data=None, headers=None):
        hdr = dict(headers or {})
        if auth:
            token = self.variables["books_webdav_username"] + ":" + self.variables["books_webdav_password"]
            hdr["Authorization"] = "Basic " + base64.b64encode(token.encode()).decode()
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}",
                                     method=method, headers=hdr, data=data)
        try:
            return self.opener.open(req, timeout=10)
        except urllib.error.HTTPError as error:
            return error

    def test_browse_download_read_only_and_idempotency(self):
        output = self.run_role()
        self.assertNotIn(self.variables["books_webdav_password"], output)
        self.assertEqual(self.request(auth=False).status, 401)
        listing = self.request(method="PROPFIND", headers={"Depth": "1"})
        self.assertEqual(listing.status, 207)
        self.assertIn(b"A%20book.epub", listing.read())
        self.assertEqual(self.request("/A%20book.epub").read(), b"EPUB fixture content")
        self.assertEqual(self.request("/A%20book.epub", method="HEAD").status, 200)
        partial = self.request("/A%20book.epub", headers={"Range": "bytes=0-3"})
        self.assertEqual(partial.status, 206)
        self.assertEqual(partial.read(), b"EPUB")
        for path in ["/private-audiobook.mp3", "/../private-audiobook.mp3", "/%2e%2e/private-audiobook.mp3"]:
            self.assertNotEqual(self.request(path).status, 200)
        for method, path, body, headers in [
            ("PUT", "/new.epub", b"blocked", {}),
            ("DELETE", "/A%20book.epub", None, {}),
            ("MKCOL", "/new", None, {}),
            ("MOVE", "/A%20book.epub", None, {"Destination": f"http://127.0.0.1:{self.port}/moved.epub"}),
        ]:
            with self.subTest(method=method):
                self.assertGreaterEqual(self.request(path, method, data=body, headers=headers).status, 400)
        self.assertEqual((self.ebooks / "A book.epub").read_bytes(), b"EPUB fixture content")
        self.assertFalse((self.ebooks / "new.epub").exists())
        unit = self.unit.read_text()
        self.assertNotIn(self.variables["books_webdav_password"], unit)
        verify = subprocess.run(["systemd-analyze", "verify", str(self.unit)], capture_output=True, text=True)
        self.assertEqual(verify.returncode, 0, verify.stderr)
        credentials = self.root / "service-state" / "credentials"
        if os.getuid() == 0:
            self.assertEqual(credentials.stat().st_mode & 0o777, 0o600)
        self.assertRegex(self.run_role(), r"changed=0\s")
        self.assertRegex(self.run_role(check=True), r"changed=0\s")
        self.variables["books_webdav_password"] = "test-only-rotated-password"
        self.run_role()
        self.assertEqual(self.request().status, 200)

    def test_fresh_check_mode_does_not_install_service(self):
        self.run_role(check=True)
        self.assertFalse(self.unit.exists())
        self.assertFalse((self.root / "service-state").exists())

    def test_explicit_write_enable_still_requires_correct_credentials(self):
        self.run_role({"books_webdav_read_only": False})
        wrong = "Basic " + base64.b64encode(b"reader:wrong-password").decode()
        denied = self.request("/new.epub", "PUT", auth=False, data=b"blocked",
                              headers={"Authorization": wrong})
        self.assertEqual(denied.status, 401)
        self.assertFalse((self.ebooks / "new.epub").exists())
        self.assertEqual(self.request("/new.epub", "PUT", data=b"allowed").status, 201)
        self.assertEqual(self.request("/new.epub").read(), b"allowed")
        credentials = self.root / "service-state" / "credentials"
        self.assertEqual(credentials.stat().st_mode & 0o777, 0o600)
        self.assertNotIn(self.variables["books_webdav_password"], credentials.read_text())
        self.assertTrue(credentials.read_text().startswith("reader:$2"))

    def test_invalid_settings_do_not_install_service(self):
        for override in [
            {"books_webdav_password": ""},
            {"books_webdav_ebook_path": "../Audiobooks"},
            {"books_webdav_ebook_path": ""},
            {"books_webdav_ebook_path": "."},
            {"books_webdav_ebook_path": "missing"},
            {"books_webdav_bind_address": "0.0.0.0"},
        ]:
            with self.subTest(override=override):
                self.run_role(override, success=False)
                self.assertFalse(self.unit.exists())
                self.assertFalse((self.root / "service-state").exists())

    def test_traefik_route_and_idempotency(self):
        # Bind to the actual private host interface; no public listener is created.
        addresses = subprocess.check_output(["hostname", "-I"], text=True).split()
        address = next((ip for ip in addresses if ip.startswith(("10.", "172.", "192.168."))), None)
        if address is None:
            self.skipTest("No private IPv4 address available")
        route_dir = self.root / "traefik"
        route_dir.mkdir()
        settings = {
            "books_webdav_traefik_enabled": True,
            "books_webdav_bind_address": address,
            "books_webdav_hostname": "books.example.com",
            "books_webdav_traefik_directory": str(route_dir),
        }
        self.run_role(settings)
        route = yaml.safe_load((route_dir / (self.service + ".yml")).read_text())["http"]
        self.assertEqual(route["routers"][self.service]["rule"], "Host(`books.example.com`)")
        self.assertEqual(route["routers"][self.service]["tls"], {})
        self.assertEqual(route["services"][self.service]["loadBalancer"]["servers"],
                         [{"url": f"http://{address}:{self.port}"}])
        self.assertRegex(self.run_role(settings), r"changed=0\s")


if __name__ == "__main__":
    unittest.main()
