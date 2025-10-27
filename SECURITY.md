# SECURITY.md

## Security Policy

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0     | :x:                |

---

## Reporting a Vulnerability

If you discover a security vulnerability in CoinScan, **please do not open a public issue**.  
Instead, report it privately to the maintainer:

- **Email:** Daniel.Riel@prosegur.com

We will respond as quickly as possible and coordinate a fix.

---

## Security Best Practices

- **Run Locally:** Only run CoinScan on trusted machines. The application accesses your webcam and local files.
- **Dependencies:** Ensure you install dependencies (OpenCV, Pillow, Tkinter) from official sources (e.g., PyPI).
- **No Network Transmission:** CoinScan does not transmit data over the internet. If you modify the code to add network features, review for security risks.
- **Webcam Access:** The application accesses your webcam. Always close the app when not in use to prevent unauthorized access.
- **File Handling:** The app does not write files by default. If you add file saving features, validate all file paths and sanitize user input.

---

## Responsible Disclosure

We encourage responsible disclosure. Please provide as much information as possible, including:

- Steps to reproduce the vulnerability
- Potential impact
- Any suggested fixes

---

## Maintainer Contact

- **Daniel Riel**  
  Daniel.Riel@prosegur.com
