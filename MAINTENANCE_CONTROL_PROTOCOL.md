# KODYS Application – Maintenance Control Protocol (MCP)
## Diagnostic & Remediation Protocol for "Farm Breaks"

This protocol defines the standard operating procedures (SOP) for identifying and resolving application failures ("Breaks") when deployed across diverse clinical environments ("The Farm").

---

### Phase 1: Diagnostic Visibility (The "Find")
When a client reports a failure, check these visibility layers first:

1.  **Visual Failures (PyQt Popups)**:
    -   If the backend or CEF fails to initialize, a visual error popup will now appear. Ask the client for a screenshot of this.
2.  **Early Boot Log (`%TEMP%\KodysFootClinikV2\kodys_boot_debug.log`)**:
    -   Captures PyQt import errors, pathing issues, and initial port binding.
3.  **App Runtime Log (`%TEMP%\KodysFootClinikV2\logs\app.log`)**:
    -   Captures Django backend errors, database migration failures, and API logic issues.
4.  **CEF Debug Log (`%TEMP%\KodysFootClinikV2\cef_debug.log`)**:
    -   Captures Chromium rendering errors or white-screen hangs.

---

### Phase 2: Common "Farm Break" Patterns & Fixes

| Break Pattern | Symptom | Diagnostic Tool | Primary Fix |
|:---|:---|:---|:---|
| **Port Collision** | App hangs at "Waiting for backend..." | `netstat -ano \| findstr :5427` | Shifted to **5427** to avoid common conflicts (Ngrok). |
| **Permission Denied** | "Access is denied" on launch or save. | `launch_error.log` (Errno 13) | **Redirection**: Moved all logs, DB, and cache to `AppData`. |
| **DLL Missing** | "Specified module could not be found." | Visual Popup (Fatal Error) | **Env Injection**: Explicitly pass `PATH` to Django subprocess. |
| **Schema Mismatch** | "No such table: auth_user" | `app.log` | **Auto-Migration**: `migrate` is now part of the `run.py` boot. |
| **Silent Crash** | Window opens then immediately closes. | `kodys_boot_debug.log` | Check for missing VC++ Redistributables or PyQt DLLs. |

---

### Phase 3: Field Remediation Strategy

1.  **Isolation (If failure persists)**:
    -   Ask the client to check if port **5427** is in use by another medical service.
2.  **Data Extraction**:
    -   The user's database is safely located in `%TEMP%\KodysFootClinikV2\db.sqlite3`. This can be copied as a backup if the app needs re-installation.
3.  **Forced Deployment**:
    -   If a manual fix is needed, always update the **`v2.2.12-GOLD-DEFINITIVE`** tag and ask the client to re-run the `git pull` sequence.

---

### Phase 4: Maintenance Checklist for New Features
Before merging any new "Farm" feature, verify:
- [ ] No file writes occur inside the installation directory (`Program Files`).
- [ ] Any new dependency (e.g., a new DLL) is explicitly added to the `PATH` in `run.py`.
- [ ] All new database tables have corresponding migrations that run automatically on boot.
- [ ] Error handlers use the `show_fatal_error()` visual reporter for end-user visibility.

---

*Document Version: 1.0 (March 2026)*
*Author: Antigravity*
