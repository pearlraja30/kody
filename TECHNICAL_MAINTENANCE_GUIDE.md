# KODYS Application – Technical Maintenance & Fix Documentation (2026/v2.2.30)

This document serves as a comprehensive guide for developers maintained the KODYS Medical Desktop Application. It includes a detailed audit of reported issues, technical implementation details, and architecture overview.

---

> [!TIP]
> **Maintenance Control Protocol (MCP)**: For a detailed guide on finding and fixing field application "breaks" (Diagnostic SOPs), see the [MAINTENANCE_CONTROL_PROTOCOL.md](file:///Users/rajasekaran/Projects/live/kody/MAINTENANCE_CONTROL_PROTOCOL.md).

---

## 1. System Architecture Overview

### Stack
- **Backend**: Python 2.7.18 / Django 1.11.29
- **Frontend**: HTML5, CSS (W3.CSS), JavaScript (jQuery, D3.js, Chart.js)
- **Desktop Wrapper**: PyQt4 with CEFPython (Chromium Embedded Framework)
- **Database**: SQLite3
- **Installer**: Inno Setup (ISCC)

### Key Files & Responsibilities
| File | Responsibility |
|------|----------------|
| `run.py` | Entry point. Encapsulated `start_application()` loop for deferred PyQt/CEF initialization. |
| `app/appsource/kodys/app_api.py` | Core business logic, signal processing (ECG), and database operations. |
| `app/appsource/kodys/views.py` | Django views handling URL routing and template rendering. |
| `app/app_assets/media/css/kodys1.css` | Global styling, layout stabilization, and responsive offsets. |
| `installer_config.iss` | Windows Installer configuration (Inno Setup). |
| `.github/workflows/build-release.yml` | CI/CD pipeline for automated multi-platform builds. |

---

## 2. Issue Audit & Resolution Status

### Section A: 20 Reported Issues

| # | Issue | Status | Resolution / Details |
|---|---|---|---|
| 1 | OS Compatibility | ✅ Fixed | Migrated to relative paths and Docker-ready architecture. |
| 2 | Startup Speed | ✅ Fixed | Optimized asset loading via relative `MEDIA_URL`. |
| 3 | CAN Report View Speed | ✅ Fixed | Implemented pre-computation of ECG data at submission. |
| 4 | CAN Report Generation | ✅ Fixed | Corrected Butterworth bandpass and notch filters. |
| 5 | PDF Export Problem | 🔧 Applied | Fixed library dependencies (pdf2image); needs `wkhtmltopdf`. |
| 6 | ECG Graph Plot Issue | ✅ Fixed | Corrected SVG gridline visibility and matplotlib backend. |
| 7 | Printing Problem | ✅ Fixed | Added centered A4 positioning and print media queries. |
| 8 | Poincare/Histogram | ✅ Fixed | Corrected mathematical derivation of R-R intervals. |
| 9 | Baseline Wandering | ✅ Fixed | Applied 0.5Hz high-pass filter to remove DC drift. |
| 10 | Pan Tompkins Alg | ✅ Fixed | Optimized integration window for 250Hz sampling. |
| 11 | Diagnose Time Delay | 🔬 Hardware | Potential latency in serial buffer; needs hardware testing. |
| 12 | Excel Export | ✅ Fixed | Implemented Pandas-based `.xlsx` export for patients. |
| 13 | DB Backup Option | ✅ Fixed | Added `download_db_backup` view in `views.py`. |
| 14 | Interpretations | 🔧 Applied | Logic added; clinical text content needs final medical review. |
| 15 | USB Detection | 🔬 Hardware | Heartbeat logic drafted; needs serial port for verification. |
| 16 | ABI & TBI Calc | ✅ Fixed | Added zero-division protection and verified ABI logic formulas. |
| 17 | VPT/HCP Report | 🔧 Applied | Visual structure refined; pending final client design mockups. |
| 18 | License Update | ⏳ Pending | Code structure ready for appending product license keys. |
| 19 | Patient Name Search | ✅ Fixed | Verified search across Name, Last Name, Surname, and ID. |
| 20 | Email Configuration | ✅ Fixed | Added connection timeout handlers and redundant SMTP fallback. |

### Section B: 7 Additional Requirements

| # | Requirement | Status | Resolution / Details |
|---|---|---|---|
| 1 | 2 More BP Measurements | 🔧 Applied | Backend fields added; UI inputs extended. |
| 2 | ECG Grid Background (Red) | ✅ Fixed | Implemented visible pink/red major/minor gridlines. |
| 3 | Baseline Removal (RT) | ✅ Fixed | Integrated high-pass filter into real-time pipeline. |
| 4 | Power Line Notch (RT) | ✅ Fixed | Integrated 50Hz IIR notch filter. |
| 5 | Histogram Code | ✅ Fixed | Corrected BPM binning and distribution plotting. |
| 6 | Poincare Code | ✅ Fixed | Corrected RRn vs RRn+1 scatter mapping. |
| 7 | QT Interval | ⏳ Research | Requires complex T-wave end detection algorithm. |

---

## 3. Deployment & CI/CD Guide

### Automated Builds
Every push to the repository triggers an automated build via GitHub Actions:
- **Windows**: Compiles the app and generates a `.exe` installer via Inno Setup.
- **Mac**: Packages the app into a portable `.zip` (Docker recommended for MacOS deployment).

### Versioning Protocol
Starting from `v2.2.5-Gold-v9`, the system uses **Detailed Versioning**:
- **Filename**: `Kodys_Foot_Clinik_[VERSION]-rev-[SHA]-[DATE].exe`
- **Current Stable**: `v2.2.30` (Zero-Write Architecture)
- **Purpose**: Prevents confusion between incremental hotfixes.

### Zero-Write Enforcement
To support read-only environments (Program Files), the deployment strategy enforces:
1. **Bytecode Suppression**: `PYTHONDONTWRITEBYTECODE=1` set at launch.
2. **Path Hardening**: Absolute path resolution in `launchapp.bat` to bypass system Python pollution.
3. **AppData Redirection**: All writable assets (DB, Logs, Media) are redirected to `%LOCALAPPDATA%\KodysFootClinikV2`.

---

## 4. Developer Onboarding Tips

### Indentation Convention
> [!IMPORTANT]
> The codebase uses **Tabs** for primary indentation. Avoid mixing spaces to prevent Python `IndentationError`.

### CEF Context
When modifying UI pages:
- Use `app.processEvents()` in loops if you need the UI to remain responsive during heavy tasks.
- The `z-index` for the sticky header is set to `10000` to prevent collision with suggestion lists.

### Database Maintenance
- SQLite is stored in `app/appsource/db.sqlite3`.
- Backups can be triggered via the Maintenance panel (creates a `.db.backup` file).

---

## 5. Sample Data & Robust Reporting

### Generating Sample Reports
To verify report templates without real hardware, you can inject \"Gold Standard\" sample data into the database.
1.  Navigate to the project root.
2.  Run the following command (requires Python 2.7 environment or `sqlite3` driver):
    ```bash
    sqlite3 app/appsource/db.sqlite3 < seed_samples_v2.sql
    ```
3.  **Search for Patient**: `P-GOLD-001` (John Doe).
4.  **View Reports**: Look for reports starting with `REP-GOLD-...`.

### Robust Reporting Mechanism
The reporting engine (`report_view` in `app_api.py`) has been upgraded with **Defensive Coding**:
- **Partial Data Handling**: If a test was saved but is missing specific readings (e.g., incomplete probe placement), the report will still generate instead of crashing.
- **Malformed JSON Protection**: Handles legacy data or manual database edits gracefully using `try/except` blocks during JSON parsing.
- **Safe List Access**: Before accessing raw ECG/CAN data by index, the system now verifies the presence of mandatory peaks to prevent `IndexError`.

> [!TIP]
> Always use `P-GOLD-001` for client demonstrations to show a fully populated set of reports for all applications (Doppler, VPT, HCP, CAN).
