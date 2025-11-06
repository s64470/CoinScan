# SECURITY.md

## Security Policy

### Supported Versions

CoinScan follows semantic versioning. The latest minor/patch of the most recent major version is supported.

| Version Branch | Status        | Notes                         |
| -------------- | ------------- | ----------------------------- |
| 1.0.0          | Supported     | Security + critical bug fixes |

---

## Reporting a Vulnerability

If you discover a security vulnerability in CoinScan, **do not open a public issue**. Report it privately to the maintainer:

- Email: Daniel.Riel@prosegur.com

### Recommended Report Format
Include (as applicable):
- A clear description of the issue and potential impact
- Steps to reproduce (screenshots / PoC code)
- Affected version (e.g., 1.1.0) and environment (OS, Python version)
- Logs or stack traces (sanitized)
- Suggested remediation (if any)

### Response & Disclosure Timeline (Target)
| Phase                | Target Timeframe |
| -------------------- | ---------------- |
| Acknowledgement      | 2 business days  |
| Initial assessment   | 5 business days  |
| Fix development      | 10 business days |
| Coordinated release  | As soon as safe  |

If timelines cannot be met you will be informed.

### Coordinated Disclosure Steps
1. You report privately.
2. Maintainer validates severity (informational / low / medium / high / critical using CVSS principles).
3. Fix is prepared; may request clarifications.
4. A patched release is published; you are notified prior to public mention.
5. (Optional) Credit given in release notes if desired.

No monetary bug bounty program is currently offered.

### CVSS Principles (v3.1)
We use CVSS v3.1 Base Score as a guideline for severity classification.

| CVSS Base Score | Mapped Severity |
| --------------- | --------------- |
| 0.0             | Informational   |
| 0.1 - 3.9       | Low             |
| 4.0 - 6.9       | Medium          |
| 7.0 - 8.9       | High            |
| 9.0 - 10.0      | Critical        |

Reporters are encouraged (optional) to provide a candidate CVSS Base Vector string.

Base Metrics (definitions simplified):
- AV (Attack Vector): Network (N), Adjacent (A), Local (L), Physical (P)
- AC (Attack Complexity): Low (L) / High (H)
- PR (Privileges Required): None (N) / Low (L) / High (H)
- UI (User Interaction): None (N) / Required (R)
- S (Scope): Unchanged (U) / Changed (C)
- C (Confidentiality Impact): None (N) / Low (L) / High (H)
- I (Integrity Impact): None (N) / Low (L) / High (H)
- A (Availability Impact): None (N) / Low (L) / High (H)

Example Base Vector: `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N`

We may adjust provided vectors after validation. Environmental/Temporal scores are not typically used unless materially changing severity.

---

## Security Best Practices

- Run Locally: Only run CoinScan on trusted machines. It accesses your webcam and local files.
- Least Privilege: Do not run as Administrator/root unless required.
- Dependencies: Install only from official sources (PyPI) and verify integrity when possible (hash pinning).
- No Network Transmission: CoinScan is offline by design. Adding network features requires auditing input/output handling, authentication, and encryption.
- Webcam Access: Close the application when not in use to reduce risk of unauthorized access.
- File Handling: Currently no file write by default. If adding persistence/export features, validate and sanitize all user-provided paths.
- Secrets: CoinScan should not require credentials or API keys. Never hard-code secrets.

---

## Maintainer Contact

- Daniel Riel  
  Daniel.Riel@prosegur.com

If you do not receive acknowledgement within 5 business days, you may resend the report with HIGH PRIORITY in the subject.