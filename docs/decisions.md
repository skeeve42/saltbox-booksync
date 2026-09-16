# Architectural Decisions

This document records significant architectural decisions for Booksync.

The goal is to preserve why decisions were made so future contributors and coding agents do not need to reconstruct the reasoning from chat history or Git commits.

---

## ADR-001: Use rclone as the storage abstraction

**Status:** Accepted

Booksync will use rclone as the abstraction layer between the application stack and remote storage.

Initial storage is expected to be Google Drive, but roles should work against a generic rclone remote where practical.

### Reasons

- Saltbox already uses rclone extensively.
- rclone supports many storage providers.
- storage-provider-specific logic can remain outside Booksync.
- the project can later support Google Drive, S3, OneDrive, Dropbox, local storage, or other backends without redesigning the stack.

### Consequences

- initial OAuth authorization may remain a manual step
- Booksync must not overwrite unrelated existing rclone remotes
- role variables should refer to generic rclone remotes rather than Google Drive specifically

---

## ADR-002: Use WebDAV for ebook distribution

**Status:** Accepted

Booksync will expose the ebook library to reading devices using authenticated WebDAV.

The initial implementation is expected to use `rclone serve webdav`.

### Reasons

- KOReader supports WebDAV natively
- CrossPoint supports WebDAV through its plugin system
- clients can browse and download books directly
- no USB transfer is required for normal use
- rclone can expose the remote directly without requiring a separate synchronization client on each ereader

### Consequences

- WebDAV should be read-only by default
- only the ebook portion of the remote should be exposed
- TLS should be handled by the existing reverse proxy
- WebDAV credentials should be independent from KOSync credentials

---

## ADR-003: Use KOSync as the reader progress protocol

**Status:** Accepted

Reading progress synchronization will use the KOReader-compatible KOSync protocol.

### Reasons

- KOReader supports KOSync directly
- CrossPoint supports KOReader-compatible synchronization
- it allows heterogeneous reading devices to share progress
- it avoids dependence on a single ereader vendor

### Consequences

- clients should use identical source EPUB files wherever possible
- book conversion on only one device may interfere with matching
- Booksync should expose a dedicated KOSync endpoint

---

## ADR-004: Use BookBridge as the initial synchronization backend

**Status:** Accepted, subject to validation during implementation

BookBridge will be the initial backend for KOSync-compatible progress synchronization and external integrations.

### Reasons

- provides a KOSync-compatible backend
- supports StoryGraph integration
- can integrate with Audiobookshelf
- keeps tracking and synchronization logic on the server rather than on a specific reader

### Consequences

- BookBridge becomes a core dependency of the initial `booksync` role
- StoryGraph failures must not break basic KOSync functionality
- administrative and synchronization endpoints should be separable

---

## ADR-005: Reuse the existing Saltbox Audiobookshelf role

**Status:** Accepted

Booksync will not maintain its own Audiobookshelf deployment role when running under Saltbox.

### Reasons

- Saltbox Sandbox already provides a maintained Audiobookshelf role
- duplication would increase maintenance burden
- Booksync should focus on integration rather than replacing existing infrastructure

### Consequences

- Audiobookshelf is an optional external dependency
- Booksync should provide integration variables and documentation
- standalone deployments may need a separate installation path later

---

## ADR-006: Support Saltbox first, standalone Ansible second

**Status:** Accepted

The primary deployment target is Saltbox, but roles should avoid unnecessary Saltbox-specific coupling.

### Reasons

- the initial deployment environment is Saltbox
- Saltbox already provides Traefik, Docker networking, DNS, users, and related infrastructure
- reusable Ansible roles make the project useful outside Saltbox

### Consequences

- Saltbox support takes priority during early development
- Saltbox-specific tasks should be isolated where practical
- role defaults and variable names should remain generic

---

## ADR-007: Use Booksync as the public synchronization namespace

**Status:** Accepted

The project and synchronization service will use the name `booksync`.

Naming conventions:

```text
Repository:
saltbox-booksync

Ansible roles:
books_rclone
books_webdav
booksync
booksync_stack

Saltbox tags:
books-rclone
books-webdav
booksync
booksync-stack

Example endpoints:
books.example.com
booksync.example.com
booksync-admin.example.com
```

### Reasons

- avoids collisions with generic names such as `sync`
- clearly communicates the service purpose
- works well for DNS, CLI tags, and role naming

---

## Pending decisions

The following decisions are not finalized:

- whether `books_webdav` should run as a host systemd service or Docker container
- whether `books_rclone` should manage a persistent mount
- exact BookBridge container/network layout
- exact standalone reverse-proxy strategy
- Molecule test topology
- backup strategy for BookBridge state
- whether OPDS should be added in a later release
