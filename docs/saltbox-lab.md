# Saltbox lab and migration runbook

## Agreed target (2026-09-17)

Ubuntu Server 26.04.1 LTS amd64 (rebuild authorized 2026-09-18), VirtualBox,
6 vCPUs, 16 GiB RAM,
50 GB dynamically allocated disk. Active disks and snapshots stay on the local
SSD. Powered-off backups go to `R:\My Drive\Saltbox\_VM`.
Cloud upload completion must be verified before treating a backup as durable.
An export preserves a machine state, not its complete snapshot history; retain
the complete powered-off VM folder when snapshot history is required.

Host check: Windows 11 Home, i7-12700KF (12 cores/20 threads), 63.82 GiB RAM,
40.29 GiB available, C: 224.28 GiB free. Windows hypervisor/VBS already running.
Do not disable host security features as part of routine provisioning.

## Required baseline before Booksync

The production screenshot establishes these container names, not their complete
configuration or connectivity:

- authelia, authelia-redis, traefik, portainer, organizr
- plex, tautulli, kometa, autoscan
- sonarr, radarr, lidarr, overseerr, seerr
- gluetun, qbittorrent, sabnzbd, jackett, nzbhydra2

Resolve each app to the current Saltbox/Sandbox role before installation.
Preserve both Seerr and Overseerr in the inventory until their intended use is
confirmed. Record role revisions and resolved image digests: mutable image tags
in the screenshot do not reproduce an exact production version.

Use Saltbox's native rclone installation and remote/mount workflow for media.
The books shared Google Drive uses a separate named remote. Do not replace an
existing rclone configuration. No media-library duplication is planned.
Plex metadata copying remains optional, subject to size and explicit production
access. Limit caches/downloads to fit the 50 GB guest disk.

## Installation gates

Before EVERY installation stage, cleanly shut down and take a named snapshot.
Record snapshot ID, timestamp, stage, commands, revisions and validation results.

1. Empty VM: snapshot before Ubuntu installation.
2. Fresh Ubuntu: verify SSH, disk size and networking; snapshot before Saltbox bootstrap.
3. Saltbox bootstrap: configure private account/domain/inventory; validate with
   `sb validate-config`, then snapshot before `sb install preinstall`.
4. Preinstall: reconnect as the configured Saltbox user; snapshot before rclone
   remote configuration. Configure remote and mount settings before the main install.
5. Storage configuration: snapshot before the core Saltbox install and before
   each app installation group; verify the correct drives and actual mount access.
6. Full baseline: verify every app, authentication, routing, mount access and reboot recovery.
7. Only after baseline acceptance: snapshot before Booksync storage/WebDAV installation.
8. Test both readers, repeat deployment, restart, removal and snapshot restoration.
9. Separately snapshot and test progress sync once implemented.

Start with NAT and local-only SSH forwarding. Choose a LAN-reachable network and
separate test DNS/TLS names before reader testing. Do not alter production DNS.
Keep automated acquisition, deletion, upload and production webhooks disabled
until their test targets are explicitly configured. Cloud permissions and paths
must be reviewed before enabling writers.

## Saltbox integration contract

Use supported Saltbox entry points instead of recreating shared infrastructure.
`sb install rclone` installs the Saltbox rclone dependency; remote OAuth setup is
a separate workflow, not implicitly performed by that command. Verify the
current documented remote and mount workflow before implementing automation.
Booksync roles must preserve unrelated remotes and mounts, remain idempotent,
use inventory overrides, and reuse Sandbox Audiobookshelf when requested.
Never recursively invoke Saltbox's installer from inside a running Ansible role.
Standalone support should remain isolated from Saltbox-specific orchestration.

## Human inputs and private artifacts

Selected lab domain: `bretcampbell.us` (unused, supplied by user). Public NS
lookup resolves to `bella.ns.cloudflare.com` and `graham.ns.cloudflare.com`.
Production uses `robretics.us`; do not change its DNS or services.

Pending: private Cloudflare authorization for the lab zone, Google authorization for each drive, VPN
provider configuration for Gluetun, Plex claim/login, indexer/Usenet credentials,
and any MFA. Request these at the stage where needed, without putting secrets
in chat logs or this repository. Windows installer elevation may require a
human UAC response. Reader interaction remains a physical acceptance step.

## Production A to B migration (planning, not yet authorized or validated)

Inventory exact paths and sizes on A before finalizing a transfer manifest:

- Saltbox account/settings/advanced settings, inventory overrides and custom mods.
- rclone config, OAuth tokens, service-account files and any crypt passwords.
- App bind mounts/volumes and consistent database backups (commonly under `/opt`,
  but inspect actual mounts rather than assuming paths).
- Plex database/metadata and identity settings if preserving the existing server.
- Authentication users/secrets, VPN configuration, certificates where necessary,
  API keys, custom scripts, scheduled tasks and service overrides.
- Local media/download state that cannot be reconstructed from remote storage.

Transfer secrets through a private encrypted channel. Preserve ownership and
permissions. Do not copy live database files without a consistency procedure.
Record exclusions for caches and reproducible files.

Rehearse: provision B, initial data copy, isolated restore and validation, then
stop writers on A, final consistent transfer, start B and switch traffic. Define
rollback and prevent simultaneous writers. Measure the interruption before
claiming a downtime target. Snapshots do not roll back external cloud changes.

## References

- https://docs.saltbox.dev/saltbox/install/install/
- https://docs.saltbox.dev/reference/rclone-manual/
- https://docs.saltbox.dev/apps/rclone/
- https://releases.ubuntu.com/22.04.5/

## Execution record

- Host inspection complete; no existing VirtualBox/VMware installation detected.
- VirtualBox 7.2.18 installed; Ubuntu ISO SHA256 verified against Canonical's
  SHA256SUMS: `9bc6028870aef3f74f4e16b900008179e78b130e6b0b9a140635434a46aa98b0`.
- VM `Saltbox-Lab` created (UUID `07a81db3-c692-496a-897d-ccb9f26a3772`),
  50,000,000,000-byte dynamic VDI, 6 vCPUs, 16 GiB RAM, NAT.
- Snapshot `00-before-ubuntu` created before installation
  (UUID `5dd29775-d9b9-487c-8007-9c5a88d39526`).
- Unattended Ubuntu installation completed. Local SSH forwarding:
  `127.0.0.1:2222` to guest port 22. Guest account: `labadmin`.
- Credentials and SSH key are outside Git in the VM's restricted `private`
  directory. VirtualBox echoes installer passwords: suppress its output for
  future provisioning. The initial password has been rotated and administrative
  access verified. Use exact LF stdin when sending credentials from Windows;
  PowerShell/native command quoting and line endings required repair in this run.
  SSH key generation must use a genuinely empty passphrase argument, not literal
  quote characters. The current key works with noninteractive SSH.
- Ubuntu first boot and subsequent reboot verified; cloud-init completed, no
  failed services, disk reports exactly 50,000,000,000 bytes.
- Powered-off snapshot `01-clean-ubuntu-before-saltbox` created
  (UUID `dce9eb92-57e2-4342-a750-2bd9d9d10692`).
- Official bootstrap downloaded and reviewed; SHA256:
  `48cbb7e73677d7ff404a599e4d80b05fc04656eca9b1d4e00339103e9378d309`.
- Bootstrap installed `sb-go` 0.0.110, then `sb setup -b master` stopped at the
  OS compatibility gate: Ubuntu 22.04 rejected; supported versions reported as
  24.04 and 26.04. No Saltbox app baseline was installed.
- This conflicts with the published docs read during planning, which still
  listed 22.04. Do not bypass the version check or claim live Saltbox acceptance.
- User authorized a fresh Ubuntu Server 26.04 rebuild on 2026-09-18,
  superseding the intermediate 24.04 selection.
  Preserve the existing 22.04 snapshot. Changing VirtualBox's OS selector did
  not change the installed guest OS.
- The 24.04 download was not executed. Official Ubuntu 26.04.1 Server ISO
  download and checksum verification completed instead. ISO SHA256:
  `cc8a95cde20f6ced61a322420de00f10cc3c90ced545daa46cb9c1a117f1d927`.
  VirtualBox 7.2.18 does
  not list a 26.04-specific profile; the ISO determines the installed OS.
- Snapshot `02-before-ubuntu-26-rebuild` saved while powered off
  (UUID `14f44e1f-5c0a-4f06-8c6a-9aa388d45b5b`). Ubuntu 26.04.1 unattended
  installation started using the existing SSH key. Installer output is retained
  privately because VirtualBox logs the supplied password.
- VirtualBox unattended provisioning resets boot order to disk-first; with an
  existing OS, shut down and explicitly set DVD-first after preparing the media.
  This was corrected before the 26.04 installer repartitioned the lab disk.
- Private Saltbox inputs are in the VM's restricted `private` directory as
  `saltbox-lab-inputs.json`. For a Cloudflare scoped token, follow the current
  [Saltbox permission table](https://docs.saltbox.dev/reference/domain/#alternative-scoped-api-token)
  and restrict Zone Resources to the lab domain. Never copy this input file into Git.
- Ubuntu 26.04.1 installation completed; kernel `7.0.0-31-generic`, exact 50 GB
  disk, SSH key login and sudo verified, no failed systemd units. Installer
  reported a transient CPU stall but completed and rebooted successfully.
  Boot log includes VirtualBox VMSVGA compatibility messages and IPv6 NTP
  connection failures; time synchronization still needs checking before TLS.
- Powered-off snapshot `03-ubuntu26-before-saltbox` created
  (UUID `14289e19-ae57-4606-893e-ee9509cc9f44`).
- Reboot verified on 26.04; NTP synchronized successfully despite initial IPv6
  connection messages. Saltbox bootstrap completed with `sb-go` 0.0.110,
  Saltbox revision `7a22a30c1e6153ae21bdc15f9c13598547455984`.
- Lab account settings installed privately and `sb validate-config` passed.
  Cloudflare credentials remain blank pending user input; validation passing
  with blank optional credentials does not prove Cloudflare authorization.
- Cloudflare confirmed by user for both lab and production domains.
- Saltbox configuration, cloud connections and all application acceptance tests
  remain pending.

### Continuation on 2026-09-18

- Reconnected to Ubuntu 26.04.1 and verified no failed systemd services.
- Confirmed powered-off snapshot `04-before-saltbox-preinstall`
  (`f5d4c542-bde0-4cb5-86d8-7633a7760c0f`) from the previous session.
- Ran `sb validate-config` and `sudo sb install preinstall` against Saltbox
  revision `7a22a30c1e6153ae21bdc15f9c13598547455984`.
  Result: 126 ok, 31 changed, 80 skipped, zero failed/unreachable/rescued/ignored.
  Installed rclone 1.75.1 and prepared the existing `labadmin` account.
- Took powered-off snapshot `05-preinstall-before-cloud-config`
  (`adc88e55-ba9b-467a-9268-f5727ccd4840`) and restarted successfully.
- Detected clock drift before shutdown. After reboot, chrony reported normal
  synchronization, sub-millisecond system offset, and `NTPSynchronized=yes`.
  Recheck time after host sleep/resume and before TLS/OAuth operations.
- Prepared `/opt/mount-templates/custom/lab-google-readonly.j2` from the installed
  Saltbox Google template with `--read-only`. Selected its absolute path in
  `settings.yml`, disabled uploads, and kept VFS disk caching disabled with a 2G
  ceiling if enabled later. Cloud mounts have not yet been deployed or tested.
- User supplied a Cloudflare token privately. Normalized the input field name
  from `scoped_token` to `cloudflare_scoped_token`, installed it in the VM's
  mode-0600 `accounts.yml`, and passed `sb validate-config` including Cloudflare
  credential validation. No DNS records were changed in this step.
- Verified direct Cloudflare API lookup returns the active `bretcampbell.us`
  zone. No production domain settings were accessed or changed.
- Completed browser authorization for two Google accounts, both with
  `drive.readonly` scope. Credentials reside in mode-0600
  `/home/labadmin/.config/rclone/rclone.conf`.
  `books` targets the first account's `Books` shared drive, containing
  `abooks/`, `ebooks/`, and `import/`. The second account supplies `google`
  (PlexCloudServers Media Part 1), `google2` (Media Part 2), and `remux` (Remux).
  Media Part 1 and Part 2 contain `Media/`; Remux contains `Remux/`.
  NFO and the second account's Books drives were not configured.
- Configured all four mounts read-only; media mounts join Saltbox's union,
  while `books` stays separate. Uploads, scheduled recursive VFS refresh,
  and VFS disk caching are disabled. Cache ceiling is 2G if later enabled.
- Private Saltbox host overrides in `inventories/host_vars/localhost.yml`:
  `use_cloudplow: false`, `skip_dns: true`, `cloudflare_records_enabled: false`,
  `rclone_vfs_cache_min_free_space: 10G`, `rclone_enable_metrics: true`
  (enables authentication for rclone remote control). DNS certificate
  challenges remain available; public A/AAAA record management is deferred
  until the lab's LAN routing is configured.
- Rclone warns that its shared Google OAuth client is being retired during
  2026. These working authorizations are provisional: create a personal Google
  OAuth client and reauthorize before treating the setup as durable.
- Powered-off snapshot `06-cloud-config-before-core` saved
  (`74f32ecf-1b50-4f45-b84d-bb58191e7354`). Started `sb install core` as
  `labadmin`; private output is `/home/labadmin/private/core-install.log`.
  The initial SSH connection timed out before starting; retried after confirming
  SSH availability. Core completed: 700 ok, 142 changed, 424 skipped, zero
  failed/unreachable/rescued/ignored. Docker, Traefik, Authelia, and its Redis
  container started; Authelia reported healthy. Application acceptance is pending.
- Verified all four live rclone mounts have kernel `ro` options and the merged
  `/mnt/unionfs/Media`, `/mnt/unionfs/Remux`, and separate books directories are
  accessible. Initial cold mount lookups were slow; measure reader latency later.
- Sandbox revision resolved to `377cb190f0286c332d98b1b0314ec3b628eea64f`.
  All baseline apps have Saltbox roles except Kometa, which uses Sandbox.
- User supplied Proton WireGuard configuration privately with NAT-PMP enabled.
  Added private Gluetun Proton/WireGuard settings and
  `qbittorrent_docker_network_mode: container:gluetun`. VPN and download client
  health still require installation and validation. No downloads are configured.
- Core masked the MOTD news timer, leaving a failed status; cleared that status
  before shutdown. Recheck systemd health on the next boot.
- Powered-off snapshot `07-core-before-proton-vpn` saved
  (`47170cad-a88b-4efc-8636-443091d8a204`). Post-core boot took about two minutes
  before SSH was usable; do not launch install commands immediately after VM
  start. Saltbox's controller then resumed the web containers automatically.
  Confirmed zero failed systemd units, synchronized time, all four read-only
  mounts, and `https://login.bretcampbell.us` returning HTTP 200 with certificate
  validation enabled using a local address override.
- `sb install gluetun` completed (71 ok, 9 changed, zero failures), but initial
  Proton automatic-server selection produced DNS timeout health-check failures.
  Do not treat an installer success as VPN acceptance. Repairing with Gluetun's
  custom WireGuard provider using the exact endpoint/public key in the supplied
  configuration and explicit Proton port-forwarding provider. qBittorrent has
  not been installed. Logs remain private as `vpn-install.log` and `vpn-repair.log`.
- VPN repair completed (71 ok, 7 changed, zero failures). Gluetun reports
  healthy and an HTTPS egress check returned its Proton public IP. NAT-PMP
  initially returned connection refused; a working tunnel does not establish
  that inbound port forwarding works. Recheck forwarded-port allocation.
- Powered-off snapshot `08-vpn-before-apps-and-lan` saved
  (`ebbbcbfa-01a8-47ac-b329-1e5d497b3364`). Added VirtualBox adapter 2 bridged
  to the active Realtek Ethernet interface; kept NAT adapter 1 and local-only
  SSH forwarding. Guest configuration and LAN access validation remain pending.
- Guest automatically obtained `192.168.10.152/24` on `enp0s8`
  (MAC `08:00:27:0e:a2:07`), with NAT still the preferred default route.
  Created only `*.bretcampbell.us` as a DNS-only A record to that private IP
  (TTL 300), after confirming no wildcard conflict. Browser verified the
  Authelia sign-in page at `https://login.bretcampbell.us` from the Windows host.
  Reserve this MAC/IP in the home router before relying on stable reader URLs;
  no DHCP reservation or router forwarding has been configured.
- Started app group with `sb install
  portainer,organizr,qbittorrent,sabnzbd,jackett,nzbhydra2,sonarr,radarr,lidarr,overseerr,seerr`.
  Private log: `/home/labadmin/private/apps-install.log`. Completion is pending.
  Initial Seerr image pull was slow but actively downloading.
- Proton tunnel recovered healthy after reboot, but NAT-PMP still returned
  connection refused and no forwarded-port file existed. Requested a new
  configuration for a different P2P server with NAT-PMP enabled. This does not
  block installation of the other applications.

### Continuation on 2026-09-19

- Found VM in saved state and resumed it headlessly. The app installer was
  still running and resumed normally; do not start a second Ansible process.
  Seerr, Portainer, Organizr, Sonarr, Radarr, and Lidarr were running; the rest
  of the requested app group was still installing. About 36G remained free.
- Saved-state resume left the guest clock several hours behind, despite an
  initially stale `NTPSynchronized=yes` flag. Restarted chrony and confirmed a
  fresh NTP reference, normal leap status, and correct UTC date/time.
- Changed the lab's `/etc/chrony/chrony.conf` from `makestep 1 3` to
  `makestep 1 -1` so large offsets can be corrected after subsequent resumes.
  Validated configuration with `chronyd -p` and restarted chrony. Original
  config retained privately at `/home/labadmin/private/chrony.conf.before-resume-fix`.
  Future saved-state resume acceptance still needs testing.
- Proton configuration file had not changed since the initial supplied file;
  replacement P2P/NAT-PMP configuration and personal Google OAuth client remain
  pending, along with Usenet/indexer details and Plex/Kometa setup inputs.
- App group completed: 445 ok, 56 changed, 108 skipped, zero failures or
  unreachable hosts. All 15 containers were running. Captured exact image IDs
  and repository digests privately in
  `/home/labadmin/private/app-image-manifest.json`.
- Sonarr, Radarr, and Lidarr authenticated API checks passed. All twelve
  tested HTTPS routes returned successful pages or redirects with valid TLS.
  Redirect checks establish routing, not completion of each app's setup wizard.
- Verified qBittorrent 5.2.3 shares Gluetun's network namespace, authenticated
  with the lab credentials, and set its network interface to `tun0` with UPnP
  disabled. Read-back confirmed both settings and an empty torrent queue.
  This version returns HTTP 204 with a session cookie on successful login.
- Prepared a private Plex browser authorization request. Opening its sign-in
  link was blocked by automatic approval review pending explicit Plex approval;
  requested that approval. No Plex account has been authorized yet.
- Saved powered-off snapshot `09-apps-before-plex`
  (`24cb6b9a-4e37-4cf7-a5c4-9cb29a967d0b`) and restarted the VM headlessly.
- Reboot verification passed: all 15 containers returned, Gluetun and Authelia
  reported healthy, all four cloud mounts remained read-only, no systemd units
  failed, and the login endpoint returned HTTP 200 with verified TLS.
  qBittorrent's `Session\Interface=tun0` persisted. Docker has an intentional
  120-second pre-start delay; allow that plus container startup before checking.
