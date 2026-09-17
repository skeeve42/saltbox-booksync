# WebDAV client acceptance

Status: instructions prepared; physical devices and the live Saltbox endpoint
have not been tested. Protocol integration tests are not device certification.

## Server preflight

1. Put a known EPUB in the configured `Books/Ebooks` subtree and record its SHA-256.
2. Run `mod-books-rclone` twice against the real remote. Confirm the second run
   reports no changes and unrelated remote definitions remain intact. Rclone may
   refresh OAuth tokens; do not publish the config or token values as evidence.
3. Deploy `mod-books-webdav` twice, confirming no changes on the second run.
4. Verify `https://books.example.com/` has a trusted TLS certificate and requires
   the configured WebDAV credentials. Check that siblings such as Audiobooks
   cannot be browsed and that uploads/deletes are rejected.

## KOReader on Kobo Clara BW

From KOReader's file browser, open **Cloud storage**, add a **WebDAV** account,
and enter `https://books.example.com/` with the WebDAV username and password.
Browse and download the known EPUB, then open it. Test a filename with spaces
and a non-ASCII character as well. Record the KOReader version and results.

References: [KOReader guide](https://koreader.rocks/user_guide/) and
[cloud-storage implementation](https://github.com/koreader/koreader/blob/master/frontend/apps/cloudstorage/cloudstorage.lua).

## CrossPoint on Xteink X4 Pro

First confirm that the installed firmware supports the WebDAV client plugin.
CrossPoint's file-transfer WebDAV **server** is separate from a remote-library
client and does not establish client support by itself.

The [sd-plugins WebDAV client](https://github.com/itsthisjustin/sd-plugins) provides
a settings page for the server URL and credentials and a reader-side folder
browser/downloader. Follow that plugin's installation instructions for the
specific firmware build. Configure `https://books.example.com/`, browse, download
the same EPUB, and open it. Record firmware/plugin versions and results.

## Evidence to record

- Endpoint, test date, firmware/application/plugin versions (no passwords).
- Browsing and downloading succeed on each reader over HTTPS.
- Downloaded EPUB hashes match the source on both devices.
- Anonymous/wrong-password access and write operations fail.
- Only the ebook subtree is visible, including attempts to navigate upward.
- Second deployment is unchanged and service survives a restart.

Leave roadmap device checkboxes open until these steps succeed on both devices.
