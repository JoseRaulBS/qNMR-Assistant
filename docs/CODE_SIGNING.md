# Code Signing Policy

> **Status:** application to SignPath Foundation submitted (July 2026).
> Signing will be enabled for Windows releases once the application is approved.

Free code signing provided by [SignPath.io](https://signpath.io), certificate
by [SignPath Foundation](https://signpath.org).

## Team and roles

| Member | GitHub | Roles |
|---|---|---|
| José Raúl Belmonte | [@JoseRaulBS](https://github.com/JoseRaulBS) | Author, Reviewer, Approver |

The person responsible for code signing is the same person who develops and
maintains the project and owns this source-code repository.

## What gets signed

Only artifacts built from this repository's source code by the public
[GitHub Actions workflow](../.github/workflows/release.yml) are signed —
currently the Windows executable (`qNMR_Assistant-windows-x64.exe`) attached
to [GitHub Releases](https://github.com/JoseRaulBS/qNMR-Assistant/releases).
No third-party binaries are ever signed. Each signing request requires manual
approval by the approver.

## Build integrity

Releases are built automatically from tagged commits on GitHub-hosted runners
(Windows, Linux and macOS). The workflow definition is public and the whole
build is reproducible from the repository source. The scientific test suite
(`tests/test_formulas.py`) must pass before any artifact is built.

## Privacy policy

qNMR Assistant does not collect, transmit or store any personal data or usage
telemetry, and performs no network communication at all. User settings
(internal standards, preferences, window geometry, language) are stored
locally in the operating-system user-data folder and never leave the machine:

- Windows: `%APPDATA%\qNMR\qNMR Assistant\`
- macOS: `~/Library/Application Support/qNMR Assistant/`
- Linux: `~/.local/share/qNMR Assistant/`

The application is portable and requires no installation; removing the
executable (and, optionally, the user-data folder above) uninstalls it
completely.
