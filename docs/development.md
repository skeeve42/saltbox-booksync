# Development

## Ansible lint

GitHub Actions runs Ansible lint on every push and pull request. You can also
start the **Ansible Lint** workflow manually from the Actions tab.

The workflow checks the repository using Ansible lint 26.8.0 and Python 3.12.
Run the same version locally from the repository root before committing:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install 'ansible-lint==26.8.0'
ansible-lint
```

Use Linux, macOS, or WSL for local linting. Update the pinned action version in
`.github/workflows/ansible-lint.yml` and the version above together.

The Saltbox entry point runs `books_rclone` with the `books-rclone` tag.
Role behavior changes require tests and idempotency checks.

## Storage integration tests

On Linux/WSL, install rclone and the virtual environment above, then run:

```bash
PATH="$PWD/.venv/bin:$PATH" python3 -m unittest discover -s tests -v
```

Tests use temporary local storage and a real rclone alias remote; no cloud
credentials are needed. Run with passwordless sudo (as in CI), or as root in an
isolated test environment. Tests cover config discovery, empty roots, missing
binary/config/remote/root, invalid inputs, check mode, configuration preservation,
directory permissions, and idempotency. The Role tests workflow runs them in CI.

On Windows-mounted WSL paths, set `ANSIBLE_CONFIG="$PWD/ansible.cfg"` explicitly
when running lint because Ansible may ignore auto-discovery on writable mounts.
