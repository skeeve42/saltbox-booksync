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

The Saltbox entry point currently contains an empty foundation play. Passing
lint does not yet validate deployment behavior; role behavior changes also
require tests and idempotency checks.
