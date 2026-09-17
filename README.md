# Booksync

Booksync is an Ansible-based deployment project for building a self-hosted ebook and audiobook synchronization stack.

It is designed primarily for Saltbox environments, while keeping individual roles reusable enough to support standalone Ansible deployments where practical.

The goal is to provide a single backend for:

* browsing and downloading ebooks from cloud storage
* synchronizing reading progress across multiple ereaders
* integrating KOReader-compatible devices and applications
* updating reading progress in StoryGraph
* integrating audiobook playback and progress through Audiobookshelf
* exposing services securely through an existing reverse proxy

## Intended workflow

A typical Booksync deployment looks like this:

```text
                     Cloud Storage
                    Google Drive etc.
                          |
                        rclone
                          |
               +----------+-----------+
               |                      |
             Ebooks                Audiobooks
               |                      |
            WebDAV              Audiobookshelf
               |                      |
        +------+-------+              |
        |              |              |
   CrossPoint       KOReader          |
   Xteink X4 Pro    Kobo / others     |
        |              |              |
        +------ KOSync +--------------+
                     |
                  Booksync
                  BookBridge
                     |
                 StoryGraph
```

The architecture deliberately separates:

* **book storage**
* **book delivery**
* **reading-progress synchronization**
* **audiobook management**
* **external tracking integrations**

This allows individual components to be replaced or disabled without redesigning the entire stack.

## Current target clients

Initial development is being tested against:

* **Xteink X4 Pro**

  * CrossPoint
  * WebDAV book downloads
  * KOReader-compatible progress synchronization

* **Kobo Clara BW**

  * KOReader
  * WebDAV book downloads
  * KOSync-compatible progress synchronization

Booksync is intended to support other KOReader-compatible devices as well.

## Components

### `books_rclone`

Manages and validates the rclone configuration used for Booksync storage.

Typical responsibilities include:

* validating the configured rclone remote
* creating local storage paths
* optionally managing mounts or related services
* preserving existing Saltbox rclone configuration
* supporting a separate cloud account specifically for books and audiobooks

Example remote:

```text
books:
```

Example storage structure:

```text
Books/
├── Ebooks/
└── Audiobooks/
```

### `books_webdav`

Provides read-only WebDAV access to the ebook library.

This allows supported readers to browse and download books directly without requiring manual USB transfer.

Example endpoint:

```text
https://books.example.com
```

Expected clients include:

* CrossPoint
* KOReader

### `booksync`

Deploys and configures the reading-progress synchronization layer.

The initial implementation is expected to use BookBridge as a KOSync-compatible backend.

Responsibilities may include:

* KOReader-compatible progress synchronization
* CrossPoint synchronization
* StoryGraph integration
* Audiobookshelf integration
* protected administrative interface
* public sync-only endpoint

Example endpoints:

```text
https://booksync.example.com
https://booksync-admin.example.com
```

### `booksync_stack`

Convenience meta-role for deploying the complete Booksync stack.

Example Saltbox command:

```bash
sb install mod-booksync-stack
```

Individual components should also remain independently deployable.

Example:

```bash
sb install mod-books-rclone
sb install mod-books-webdav
sb install mod-booksync
```

## Audiobookshelf

Booksync does not intend to duplicate an existing Audiobookshelf Ansible role.

For Saltbox deployments, the existing Sandbox Audiobookshelf role should be used where possible.

Booksync will provide the integration layer between Audiobookshelf, BookBridge, and ebook progress synchronization.

## Saltbox support

Booksync is intended to work as a Saltbox Mod.

Example configuration:

```yaml
saltbox_mod_repo: "https://github.com/YOUR_USERNAME/saltbox-booksync.git"
saltbox_mod_branch: "main"
```

After installing or updating `saltbox_mod`:

```bash
sb install saltbox-mod
```

the complete stack should eventually be deployable with:

```bash
sb install mod-booksync-stack
```

The project should follow Saltbox conventions for:

* Docker networking
* Traefik
* DNS
* users and groups
* paths
* inventory overrides
* service naming

## Standalone Ansible support

Where practical, roles should avoid hard dependencies on Saltbox internals.

The long-term goal is to allow deployment outside Saltbox using a standard Ansible playbook:

```bash
ansible-playbook \
  -i inventory.ini \
  playbooks/standalone.yml
```

Saltbox-specific functionality should be provided through variables and integration tasks rather than being hard-coded throughout individual roles.

## Naming conventions

Repository:

```text
saltbox-booksync
```

Ansible roles:

```text
books_rclone
books_webdav
booksync
booksync_stack
```

Saltbox tags:

```text
books-rclone
books-webdav
booksync
booksync-stack
```

Typical service names:

```text
booksync-bookbridge
books-webdav
```

Typical DNS names:

```text
books.example.com
booksync.example.com
booksync-admin.example.com
```

Variables should use role-specific prefixes:

```yaml
books_rclone_remote: "books"
books_webdav_subdomain: "books"
booksync_subdomain: "booksync"
```

## Security

Booksync must not store credentials or session tokens in the public repository.

Secrets may include:

* Google OAuth tokens
* rclone credentials
* WebDAV credentials
* StoryGraph session credentials
* Audiobookshelf API tokens
* BookBridge credentials

Secrets should be supplied through:

* Ansible Vault
* private Saltbox inventory
* environment variables
* other supported secret-management mechanisms

Example files containing secrets should contain placeholders only.

## Development principles

The project should follow these principles:

* roles must be idempotent
* existing Saltbox configuration must not be modified unnecessarily
* existing rclone remotes must not be overwritten
* secrets must never be committed
* existing maintained Saltbox/Sandbox roles should be reused rather than duplicated
* services should expose only the endpoints they require
* ebook WebDAV access should be read-only by default
* roles should remain independently deployable
* changes should pass `ansible-lint`
* significant role behavior should have automated tests where practical

## Planned repository structure

```text
saltbox-booksync/
├── README.md
├── AGENTS.md
├── LICENSE
├── ansible.cfg
├── saltbox_mod.yml
├── requirements.yml
│
├── docs/
│   ├── architecture.md
│   ├── decisions.md
│   ├── development.md
│   └── roadmap.md
│
├── playbooks/
│   └── standalone.yml
│
├── roles/
│   ├── books_rclone/
│   ├── books_webdav/
│   ├── booksync/
│   └── booksync_stack/
│
├── molecule/
│
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/
```

## Project status

Booksync is currently in early development.

Phase 0 is complete locally. Phase 1 storage validation is implemented in
[`books_rclone`](roles/books_rclone/README.md). Phase 2 authenticated, read-only
WebDAV is implemented in [`books_webdav`](roles/books_webdav/README.md), including
systemd management, Saltbox Traefik routing, and offline integration tests.
Live Saltbox/cloud and physical reader validation remain pending; see the
[roadmap](docs/roadmap.md) and [client acceptance checklist](docs/client-validation.md).

Initial milestones are:

1. Create and validate the `books_rclone` role.
2. Deploy read-only ebook WebDAV access.
3. Verify ebook downloads from CrossPoint and KOReader.
4. Deploy a KOSync-compatible Booksync backend.
5. Verify bidirectional reading-progress synchronization.
6. Integrate StoryGraph updates.
7. Integrate Audiobookshelf.
8. Add automated testing and standalone Ansible support.

## License

A license has not yet been selected.
