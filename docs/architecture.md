# Booksync Architecture

## Overview

Booksync provides a self-hosted backend for ebook and audiobook distribution, reading-progress synchronization, and external reading-tracker integration.

The system is designed around a central server that exposes a consistent library and synchronization layer to multiple reading clients.

The primary goals are:

- keep the book library in one authoritative location
- allow multiple devices to browse and download the same source files
- synchronize reading progress across devices
- support both ebook and audiobook workflows
- update external reading services such as StoryGraph
- integrate cleanly with Saltbox
- remain reusable outside Saltbox where practical

Booksync should avoid unnecessary duplication of existing Saltbox or Sandbox roles.

---

## High-level architecture

```text
                         Cloud Storage
                        Google Drive
                             |
                           rclone
                             |
                    +--------+--------+
                    |                 |
                  Ebooks           Audiobooks
                    |                 |
             books_webdav       Audiobookshelf
                    |                 |
          +---------+---------+       |
          |                   |       |
      CrossPoint           KOReader   |
      Xteink X4 Pro        Kobo       |
          |                   |       |
          +--------+----------+       |
                   |                  |
                 KOSync               |
                   |                  |
                Booksync              |
                BookBridge -----------+
                   |
                   |
               StoryGraph
```

---

## Architectural principles

### Single source of truth

Books should originate from a single authoritative storage location.

For the initial implementation, this is expected to be a dedicated Google Drive account accessed through rclone.

Both ebook clients should download the same original book file wherever possible.

This is important because KOSync document matching may depend on the content or hash of the file.

Booksync should avoid workflows that independently convert the same book for different devices unless there is a clear reason to do so.

---

### Server-centric synchronization

Reading-progress synchronization should be managed by the server rather than relying on one specific reader.

This allows:

- either reader to be unavailable without breaking the workflow
- additional KOReader-compatible devices to be added later
- progress data to feed other services such as StoryGraph
- audiobook progress to participate in the same synchronization architecture

The sync backend should therefore be treated as an independent service.

---

### Reader independence

Booksync should not require a specific hardware vendor.

Current target clients are:

- CrossPoint on Xteink X4 Pro
- KOReader on Kobo Clara BW

However, any compatible KOSync client should be able to participate.

Device-specific setup should remain outside the core server deployment wherever possible.

---

### Reuse existing services

Booksync should not reimplement services already maintained elsewhere.

Examples:

- Audiobookshelf should use the existing Saltbox Sandbox role.
- Traefik should use Saltbox's existing reverse proxy.
- DNS should use existing Saltbox mechanisms.
- rclone should integrate with the system's existing rclone installation.

Booksync should provide integration, not duplicate existing infrastructure.

---

## Core components

## 1. `books_rclone`

Purpose:

Provide access to the authoritative book storage.

Expected responsibilities:

- validate the configured rclone remote
- ensure required local directories exist
- optionally mount book storage where required
- preserve existing Saltbox rclone remotes
- provide stable paths for dependent services

Example:

```yaml
books_rclone_remote: books
books_rclone_root: Books
books_rclone_mount_path: /mnt/books
```

Expected remote structure:

```text
books:
└── Books/
    ├── Ebooks/
    └── Audiobooks/
```

The role must never overwrite an unrelated existing rclone remote.

OAuth setup may require an initial manual authorization step.

---

## 2. `books_webdav`

Purpose:

Expose the ebook library to readers over WebDAV.

Expected implementation:

```text
rclone serve webdav
```

Initial design assumptions:

- read-only by default
- TLS termination handled by Traefik
- authentication required
- ebook storage accessed directly from the configured rclone remote
- no public unauthenticated access

Example endpoint:

```text
https://books.example.com
```

Primary clients:

- CrossPoint WebDAV plugin
- KOReader WebDAV cloud storage

The WebDAV layer should expose only the ebook library, not the entire cloud-storage account.

---

## 3. `booksync`

Purpose:

Provide reading-progress synchronization and related integrations.

The initial implementation is expected to use BookBridge.

Responsibilities may include:

- KOSync-compatible endpoint
- CrossPoint progress synchronization
- KOReader progress synchronization
- StoryGraph updates
- Audiobookshelf integration
- administration interface

Suggested endpoints:

```text
https://booksync.example.com
https://booksync-admin.example.com
```

The synchronization endpoint and administrative interface should be separable.

The administrative interface should not be exposed publicly without authentication or other access controls.

---

## 4. `booksync_stack`

Purpose:

Provide a meta-role for installing the complete Booksync stack.

Expected dependencies:

```text
books_rclone
books_webdav
booksync
```

Audiobookshelf should remain an external dependency and should not be duplicated inside this role.

Example:

```bash
sb install mod-booksync-stack
```

Individual roles must remain independently installable.

---

## Ebook flow

The expected ebook workflow is:

```text
Google Drive
    |
    v
rclone remote
    |
    v
books_webdav
    |
    +------------------+
    |                  |
    v                  v
CrossPoint          KOReader
X4 Pro              Kobo
```

A user should be able to:

1. add an EPUB to the cloud library
2. browse the library from either reader
3. download the EPUB directly
4. open the same source file on either device

No USB transfer should be required for normal operation.

---

## Reading-progress flow

The expected synchronization flow is:

```text
CrossPoint --------+
                   |
                   v
                KOSync
              BookBridge
                   ^
                   |
KOReader ----------+
```

Each device should:

- push progress when reading ends or sync is requested
- retrieve newer progress before continuing on another device

The backend should resolve progress based on KOSync-compatible book identity and position metadata.

Where possible, both devices should use identical source files to reduce matching problems.

---

## StoryGraph flow

StoryGraph updates should originate from the server.

Expected flow:

```text
Reader
  |
  v
KOSync
  |
  v
BookBridge
  |
  v
StoryGraph
```

This ensures StoryGraph updates are not dependent on a specific reader being active.

Because StoryGraph does not provide a stable public API for all required functions, integration may depend on session credentials or other unofficial mechanisms.

This integration should therefore be isolated from the core synchronization path so that a StoryGraph failure does not break book synchronization.

---

## Audiobook flow

Audiobooks should be handled by Audiobookshelf.

Expected flow:

```text
Google Drive
    |
    v
rclone
    |
    v
Audiobookshelf
    |
    v
BookBridge
    |
    v
KOSync
```

Long-term goals may include synchronizing approximate progress between:

- ebook reading
- audiobook listening

This should be treated as an optional integration.

Basic ebook synchronization must not depend on Audiobookshelf.

---

## Networking

Booksync should assume an existing HTTPS reverse proxy in Saltbox deployments.

Expected public services:

```text
books.example.com
booksync.example.com
```

Expected restricted service:

```text
booksync-admin.example.com
```

Internal ports should not be exposed directly to the Internet.

Example:

```text
Internet
   |
Traefik
   |
   +--> books.example.com
   |       |
   |       +--> books_webdav
   |
   +--> booksync.example.com
   |       |
   |       +--> KOSync endpoint
   |
   +--> booksync-admin.example.com
           |
           +--> BookBridge admin interface
```

TLS should be handled by Traefik.

---

## Authentication

Booksync should keep authentication boundaries separate.

Potential credentials include:

### WebDAV

Used by readers to access ebooks.

```text
books.example.com
```

Should have dedicated credentials.

### KOSync

Used by CrossPoint and KOReader.

```text
booksync.example.com
```

Should use separate credentials from WebDAV.

### Administration

Used for server administration.

```text
booksync-admin.example.com
```

Should use stronger access controls where practical.

---

## Secrets

No secrets should be stored in the repository.

Examples include:

- Google OAuth credentials
- rclone tokens
- WebDAV passwords
- KOSync credentials
- StoryGraph session tokens
- Audiobookshelf API tokens

Secrets should be provided through one of:

- Ansible Vault
- Saltbox private inventory
- environment variables
- external secret-management systems

Role defaults must contain placeholder or empty values only.

---

## Saltbox integration

Saltbox deployments should reuse:

- Saltbox user and group settings
- Docker network
- Traefik
- DNS configuration
- inventory
- existing service roles

Saltbox-specific logic should be isolated where practical.

Roles should avoid hard-coded assumptions such as:

```text
/srv/git/saltbox
```

unless the value is obtained through configuration.

---

## Standalone Ansible support

Booksync roles should remain reusable outside Saltbox where practical.

The expected standalone architecture is:

```text
Ubuntu / Debian host
        |
      Ansible
        |
        +--> rclone
        +--> WebDAV
        +--> BookBridge
        +--> optional reverse proxy
```

Saltbox-specific integrations should be implemented through variables or conditional task files.

For example:

```yaml
booksync_platform: saltbox
```

or:

```yaml
booksync_platform: standalone
```

The exact implementation is still to be determined.

---

## Filesystem layout

Suggested server paths:

```text
/mnt/books/
├── Ebooks/
└── Audiobooks/
```

Application state:

```text
/opt/booksync/
├── bookbridge/
├── webdav/
└── data/
```

Saltbox-specific paths may differ depending on project conventions.

Paths must be configurable.

---

## Container layout

Expected containers or services:

```text
books-webdav
booksync-bookbridge
audiobookshelf
```

Audiobookshelf is external to this project.

Where appropriate, services should join the existing Saltbox Docker network.

---

## Failure isolation

The architecture should degrade gracefully.

Examples:

If StoryGraph is unavailable:

```text
Reading sync continues.
```

If Audiobookshelf is unavailable:

```text
Ebook sync continues.
```

If WebDAV is unavailable:

```text
Already downloaded books remain readable.
KOSync may continue to work.
```

If KOSync is unavailable:

```text
Books remain readable locally.
Progress synchronization resumes when the service returns.
```

External integrations must not become hard dependencies for local reading.

---

## Idempotency

Every Ansible role must be safe to run repeatedly.

A second run should not:

- duplicate services
- modify unrelated rclone remotes
- regenerate credentials
- overwrite user content
- restart unrelated containers
- change configuration unnecessarily

Molecule or equivalent tests should verify idempotency where practical.

---

## Extensibility

Potential future integrations include:

- OPDS
- Calibre-Web
- Kavita
- additional cloud-storage providers
- Nextcloud
- additional reading trackers
- additional KOSync-compatible readers
- local NAS storage
- S3-compatible object storage

The architecture should avoid assuming Google Drive is the only supported storage backend.

Where possible, roles should operate against generic rclone remotes rather than Google Drive specifically.

---

## Architectural decisions

Significant decisions should be recorded separately in:

```text
docs/decisions.md
```

Examples:

```text
ADR-001: Use rclone as the storage abstraction
ADR-002: Use WebDAV for reader library access
ADR-003: Use KOSync as the device-sync protocol
ADR-004: Use BookBridge as the synchronization backend
ADR-005: Reuse Sandbox Audiobookshelf rather than maintaining a duplicate role
```

This file describes the current architecture.

`docs/decisions.md` should explain why major choices were made.

---

## Open questions

The following decisions are intentionally not finalized yet:

- whether `books_rclone` should mount storage or expose it directly to dependent services
- whether WebDAV should run as a systemd-managed rclone process or Docker container
- exact BookBridge container configuration
- how BookBridge metadata should map books to StoryGraph editions
- whether audiobook-to-ebook progress alignment should be enabled by default
- standalone reverse-proxy implementation
- CI and Molecule test strategy
- backup strategy for Booksync state

These should be resolved through implementation and recorded as architectural decisions.
