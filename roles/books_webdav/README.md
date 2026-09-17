# books_webdav

Runs the existing host rclone as a systemd service, serving only
`books:Books/Ebooks` by default. Authentication is mandatory and WebDAV is
read-only by default. The role includes `books_rclone` validation and validates
the ebook subdirectory before installing the service.

## Saltbox configuration

Requires Debian/Ubuntu with systemd; the role installs `apache2-utils` for bcrypt
password-file management. Install rclone and configure the remote manually first. Install Saltbox's Docker
network and Traefik before this role. Create the public DNS record pointing at
your existing Traefik server; this role does not manage DNS.

Set these overrides in private inventory (encrypt the password with Ansible Vault):

```yaml
books_rclone_remote: books
books_rclone_root: Books
books_rclone_config: /home/YOUR_USER/.config/rclone/rclone.conf
books_webdav_ebook_path: Ebooks
books_webdav_username: YOUR_WEBDAV_USER
books_webdav_password: "{{ vault_books_webdav_password }}"
books_webdav_subdomain: books
books_webdav_domain: example.com
```

Use a username containing letters, numbers, dots, underscores, `@`, or hyphens,
and a printable ASCII password of 16–72 characters (bcrypt's limit). Deploy with:

```bash
sb install mod-books-webdav
```

The service uses the storage user's identity and existing config in place, so
rclone can refresh OAuth tokens normally. The role never copies or rewrites the
rclone config. A refreshed cloud token may nevertheless be saved by rclone itself.
Encrypted configs requiring interactive passwords are not supported.

The role discovers the IPv4 gateway of Docker network `saltbox` and binds port
8087 only on that host interface. Override `books_webdav_docker_network`,
`books_webdav_bind_address`, or `books_webdav_port` for a different topology.
Allow the Traefik container to reach that address through your host firewall.
Public/wildcard listeners are rejected. Trusted containers on the bridge can
reach this HTTP backend; TLS is terminated by Traefik.

The route is written to `/opt/traefik/books-webdav.yml` in Saltbox's existing
watched file-provider directory. Override `books_webdav_traefik_directory` when
needed. It uses `websecure` and inherits its certificate resolver; set
`books_webdav_traefik_certresolver` to select another existing resolver.
It deliberately does not use interactive SSO, which readers cannot complete.

Credentials are stored as a bcrypt hash in `/opt/books-webdav/credentials`, owned
by the storage user with mode `0600` inside a `0700` directory. Plaintext passwords
are passed to the password utility on stdin, excluded from task output, and never
stored in the unit, process arguments, or environment. Changing credentials or
service settings restarts the service. The password file is dedicated to this
role and is replaced with the configured account when credentials change.

Only `books_webdav_ebook_path`, relative to `books_rclone_root`, is served.
Keep private material out of that subtree. Changing `books_webdav_read_only` to
`false` explicitly permits writes and is not needed for reader downloads.

## Checks and operations

Each deployment checks authenticated `PROPFIND` (207) and anonymous rejection
(401). Traefik checks the authentication challenge every 30 seconds; that is a
process/authentication readiness check, not an ongoing cloud-access check.
Systemd restarts a crashed process. Inspect with:

```bash
systemctl status books-webdav
journalctl -u books-webdav
```

Check mode validates storage and previews the unit/route without changing
credentials, starting/restarting the service, or making HTTP checks. A second
normal deployment should report no changes.

For standalone Linux with systemd, set `books_webdav_traefik_enabled: false`.
The service then binds to `127.0.0.1` by default; configure your own HTTPS proxy.
Use an Ansible play with gathered facts and role `books_webdav`, configuring the
storage user/group explicitly as described in the storage role README.

Keep the service name and state path stable after installation. To retire an
installation or rename it, stop/disable the old systemd unit and remove its unit,
credential directory, and Traefik route explicitly. Disabling Traefik integration
does not uninstall an earlier route.

## Reader acceptance

See [client validation](../../docs/client-validation.md). Automated tests cover
WebDAV browsing/download behavior, but physical KOReader/CrossPoint acceptance
and live Saltbox TLS/cloud validation remain pending.

Implementation references: [rclone WebDAV](https://rclone.org/commands/rclone_serve_webdav/)
and [Saltbox Traefik](https://docs.saltbox.dev/apps/traefik/).
