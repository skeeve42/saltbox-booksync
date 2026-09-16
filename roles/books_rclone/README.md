# books_rclone

Validates an existing rclone installation and books remote, then creates local
Booksync state/cache directories. No mount, service, remote creation, or OAuth
authorization is performed. Directory creation requires privilege escalation.

Set overrides in private Saltbox inventory:

```yaml
books_rclone_user: your_saltbox_user
books_rclone_group: your_saltbox_group
books_rclone_config: /home/your_saltbox_user/.config/rclone/rclone.conf
books_rclone_remote: books
books_rclone_root: Books
books_rclone_local_directories:
  - /opt/booksync
  - /opt/booksync/cache
```

Run the `books-rclone` tag through the Saltbox Mod entry point. The role can also
be included in any Linux play with facts enabled. Saltbox's `user.name` supplies
the default user/group; otherwise gathered user facts are used. Set a group
override if the user's primary group has a different name.

`books_rclone_binary` defaults to `rclone` on the target user's PATH; an absolute
executable path can be supplied. An empty `books_rclone_config` (the default)
uses `rclone config file` as the storage user, including rclone's normal config
discovery rules. Explicit paths are preferable when deploying with become.
Encrypted configuration must already have a noninteractive password mechanism
available in that user's execution environment; interactive prompting is disabled.

The role exports `books_rclone_config_path` and `books_rclone_source` for later
roles. Local directories default to mode `0750`, configurable with
`books_rclone_directory_mode`. They contain no synchronized library or mount.

Validation lists the configured root nonrecursively. Empty directories pass;
missing paths fail where the backend distinguishes them. Object storage may not
distinguish a missing prefix from an empty directory. Validation proves listing
access, not permission to download every object. Backend output is hidden to keep
credentials and book titles out of Ansible logs.

The role never writes rclone configuration or changes remote definitions. Rclone
itself may refresh and persist OAuth tokens during access checks. Existing
authorization must be set up manually. Check mode still performs read-only
validation but does not create local directories.

Offline integration tests exercise a real rclone alias remote, assert unchanged
configuration (including an unrelated remote), and verify repeat-run idempotency.
A real Saltbox/cloud acceptance run is still required before production use.

References: [config discovery](https://rclone.org/commands/rclone_config_file/)
and [directory listing](https://rclone.org/commands/rclone_lsf/).
