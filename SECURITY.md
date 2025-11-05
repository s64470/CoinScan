# SECURITY.md

# Security Policy

Thank you for helping keep CoinScan and its users safe.

## Reporting a Vulnerability

- Do NOT open a public issue for security reports.
- Preferred: Use GitHub’s private reporting flow (Security tab → Report a vulnerability / GitHub Security Advisory).
- Fallback: Email the maintainer at Daniel.Riel@prosegur.com.

Please include:

- Description and impact of the issue
- Steps to reproduce and minimal proof of concept
- Affected commit/versions and environment details (OS, Python, package versions)
- Any suggested remediation or mitigations

We will acknowledge receipt within 3 business days and keep you informed of progress.

## Coordinated Disclosure

- We follow responsible disclosure. After triage and confirmation, we will:
  - Develop and validate a fix promptly
  - Target public disclosure within 90 days, or sooner when a fix is available
  - Credit reporters who wish to be acknowledged after a fix ships
- Please refrain from public disclosure until we release a fix.

## Supported Versions

We generally provide security fixes for:

- The `master` branch (latest)
- The latest tagged release

Older releases may receive fixes on a best-effort basis only.

## Dependency Security

- Python dependencies are declared in `requirements.txt`.
- We periodically review and update dependencies to address known CVEs.
- If you discover a vulnerability in a dependency that affects CoinScan, include the exact package and version in your report.

## Project Security Notes

- CoinScan is a local GUI application that may access your webcam and local files.
- By default, it does not transmit data over the network. If you extend it with network features, review for security/privacy risks.
- When adding file I/O, validate and sanitize all file paths and user-controlled inputs.

## Safe Harbor

We support good-faith security research and will not pursue legal action for:

- Testing that avoids privacy violations, data destruction, or service degradation
- Reporting vulnerabilities via the private advisory process
- Making a good-faith effort to respect scope and not access data you do not own

## Scope

- In scope: Code in this repository and its default configurations.
- Out of scope: Vulnerabilities exclusively in third-party dependencies (report upstream), unless the impact is unique to CoinScan’s usage.

## After a Fix

- We will publish release notes that describe the issue (to a reasonable extent), impact, and upgrade guidance.
- Update to the latest version and reinstall dependencies from `requirements.txt`.

---

## Maintainer Contact

- **Daniel Riel**  
  Daniel.Riel@prosegur.com