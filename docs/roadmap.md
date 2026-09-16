# Booksync Roadmap

## Phase 0 — Repository foundation

**Goal:** Create a safe development baseline.

- [x] Create repository
- [x] Add `README.md`
- [x] Add `AGENTS.md`
- [x] Add `docs/architecture.md`
- [x] Add `docs/decisions.md`
- [x] Add `docs/roadmap.md`
- [x] Add basic Ansible project structure
- [x] Add `ansible.cfg`
- [x] Add `requirements.yml`
- [x] Add `saltbox_mod.yml`
- [x] Add CI for `ansible-lint`

---

## Phase 1 — `books_rclone`

**Goal:** Validate and expose the configured books storage safely.

Initial scope:

- [ ] detect the existing rclone installation
- [ ] locate the active rclone configuration
- [ ] validate a configured `books` remote
- [ ] validate access to the configured books root
- [ ] create required local directories
- [ ] fail clearly when the remote is missing or inaccessible
- [ ] preserve all existing rclone remotes
- [ ] avoid automating OAuth in v1
- [ ] verify idempotency
- [ ] add tests

Success criteria:

```text
An existing Saltbox server can run the role repeatedly
without modifying unrelated rclone configuration.
```

---

## Phase 2 — `books_webdav`

**Goal:** Allow supported readers to browse and download ebooks remotely.

- [ ] expose the ebook library over authenticated WebDAV
- [ ] read-only by default
- [ ] support configurable endpoint and credentials
- [ ] integrate with Saltbox Traefik
- [ ] expose only the configured ebook path
- [ ] verify KOReader access
- [ ] verify CrossPoint access
- [ ] add health checks
- [ ] verify idempotency

Success criteria:

```text
An EPUB stored in the configured rclone remote can be
browsed and downloaded from both KOReader and CrossPoint.
```

---

## Phase 3 — Client validation

**Goal:** Prove the end-to-end book delivery workflow before adding synchronization.

Target clients:

- Xteink X4 Pro with CrossPoint
- Kobo Clara BW with KOReader

- [ ] install/configure KOReader on Kobo
- [ ] configure CrossPoint WebDAV plugin
- [ ] download the same EPUB to both readers
- [ ] confirm identical source file is used
- [ ] document client setup

Success criteria:

```text
Both readers independently download and open the same EPUB
from Booksync WebDAV.
```

---

## Phase 4 — `booksync`

**Goal:** Synchronize reading progress across devices.

- [ ] deploy BookBridge
- [ ] expose KOSync endpoint
- [ ] protect administrative endpoint
- [ ] configure KOReader
- [ ] configure CrossPoint
- [ ] verify Kobo → X4 progress transfer
- [ ] verify X4 → Kobo progress transfer
- [ ] document recovery behavior when sync is unavailable
- [ ] add health checks
- [ ] verify idempotency

Success criteria:

```text
A user can stop reading on either device and continue at
the corresponding location on the other device.
```

---

## Phase 5 — StoryGraph integration

**Goal:** Update StoryGraph automatically from server-side reading progress.

- [ ] configure StoryGraph integration
- [ ] keep StoryGraph credentials out of the repository
- [ ] verify percentage updates
- [ ] verify completed-book updates
- [ ] document session-token renewal
- [ ] ensure StoryGraph failure does not affect KOSync

Success criteria:

```text
Reading progress from either reader is reflected in
StoryGraph without manual updates.
```

---

## Phase 6 — Audiobookshelf integration

**Goal:** Integrate audiobook progress without duplicating the existing Saltbox role.

- [ ] document installation of Sandbox Audiobookshelf
- [ ] expose configured audiobook storage
- [ ] configure BookBridge integration
- [ ] test audiobook progress import
- [ ] evaluate ebook ↔ audiobook alignment
- [ ] document limitations

Success criteria:

```text
Audiobook progress can participate in the Booksync
tracking workflow without affecting normal ebook sync.
```

---

## Phase 7 — Standalone Ansible support

**Goal:** Run Booksync outside Saltbox.

- [ ] add standalone playbook
- [ ] identify Saltbox-specific dependencies
- [ ] add generic Docker networking support
- [ ] add reverse-proxy configuration strategy
- [ ] document supported Linux distributions
- [ ] add standalone installation documentation

---

## Phase 8 — Hardening and release

- [ ] Molecule coverage for core roles
- [ ] GitHub Actions CI
- [ ] secret-handling documentation
- [ ] backup and restore documentation
- [ ] upgrade procedure
- [ ] rollback procedure
- [ ] example inventory
- [ ] example Vault configuration
- [ ] tagged release
- [ ] evaluate submission of suitable roles to Saltbox Sandbox

---

## Future ideas

Not part of the initial release:

- OPDS
- Calibre-Web integration
- Kavita integration
- additional reading trackers
- additional storage providers
- NAS/local-library deployment
- S3-compatible storage
- automatic book metadata normalization
- additional KOSync-compatible clients
