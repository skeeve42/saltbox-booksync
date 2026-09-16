# Booksync Agent Instructions

## Project

Booksync is an Ansible-based deployment system for a self-hosted
ebook/audiobook synchronization stack.

It supports:

- Saltbox via saltbox_mod
- standalone Ansible deployments
- rclone-backed book storage
- read-only WebDAV
- BookBridge / KOSync
- StoryGraph integration
- Audiobookshelf integration

## Naming

Repository:
saltbox-booksync

Roles:
- books_rclone
- books_webdav
- booksync
- booksync_stack

Saltbox tags:
- books-rclone
- books-webdav
- booksync
- booksync-stack

Public endpoints:
- books.example.com
- booksync.example.com
- booksync-admin.example.com

## Development rules

- Never commit credentials.
- Keep roles idempotent.
- Prefer Saltbox inventory overrides.
- Roles must remain usable outside Saltbox where practical.
- Do not duplicate existing Sandbox roles such as Audiobookshelf.
- Run ansible-lint before committing.
- Add tests for changes affecting role behavior.
