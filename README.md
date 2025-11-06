# CoinScan (MünzScan)

Version: 1.0.0

SPDX-License-Identifier: LicenseRef-Prosegur-Only

CoinScan is a lightweight desktop app that identifies and counts Euro coins using your computer’s webcam. It runs locally, offers a minimal UI with English and German languages, and supports a high-contrast mode and adjustable font sizes.

---

## Features

- Single-click scan: captures one webcam frame and runs recognition
- Heuristic recognition by coin radius (size) and mean HSV hue (colour)
- Multilingual UI: English and German (language buttons in the top bar)
- High-contrast toggle (sun/moon icon) for accessibility
- Adjustable font sizes (A− / A+)
- Responsive, Tkinter-based UI with a sidebar (Home, Settings, About, Exit)
- Runs fully offline

---

## Requirements

- Python 3.10–3.12 recommended
- A working webcam
- OS: Windows, macOS, or Linux with GUI support and Tk available

Python packages (installed via the requirements file):

- numpy
- opencv-python
- pillow (Pillow)

Note: Tkinter usually ships with Python. On some Linux distributions you may need to install it separately (e.g., `sudo apt-get install python3-tk`).

---

## Install

1. Clone the repository
2. (Optional) Create and activate a virtual environment
   - Windows (PowerShell)
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
   - macOS/Linux
     - `python3 -m venv .venv`
     - `source .venv/bin/activate`
3. Install dependencies
   - `python -m pip install -r CoinScan/requirements.txt`

---

## Run

- `python CoinScan/CoinScan.py`

On launch the app starts in fullscreen. Use F11 to toggle fullscreen and Esc to exit fullscreen. Use the flag buttons (DE/UK) to switch languages and the sun/moon button to toggle high-contrast mode.

---

## Usage

- Place one coin near the centre of the webcam view
- Click “Scan Coins” to capture one frame and run detection
- The detected coin and estimated value appear in the list; the total is shown on the right
- Use the size button to select capture resolution (currently `480x360`)
- Use A− / A+ to adjust font sizes

---

## Security and Privacy

CoinScan runs locally and does not transmit data over the network. The app accesses your webcam; close it when not in use. See `SECURITY.md` for the full security policy and how to report vulnerabilities.

---

## Contributing

Issues and pull requests are welcome. For security vulnerabilities, do not open a public issue — follow the instructions in `SECURITY.md`.

---

## Maintainer

- Daniel Riel — Daniel.Riel@prosegur.com

---

## License — Prosegur Only

CoinScan (MünzScan) is licensed for exclusive internal use by Prosegur S.A. and its affiliated entities. No other individual or organization is permitted to use, copy, distribute, or modify this software without prior written consent from the copyright holder. See `LICENSE.md` for the full terms.

Summary (not a substitute for the license):

- Allowed: internal use by Prosegur and its employees and contractors for Prosegur business purposes.
- Not allowed: use by any third party; redistribution; sublicensing; public hosting; commercial use by non‑Prosegur entities; derivative works or modifications distributed outside Prosegur without written permission.
- Conditions: retain copyright and license notices; attribute the authors; clearly mark modifications; keep the software and any derived materials internal to Prosegur.
- Warranty/Liability: provided “as is”, without warranty; limited liability as described in the license.

For any permissions beyond the above, contact Daniel Riel — Daniel.Riel@prosegur.com.