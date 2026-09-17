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
