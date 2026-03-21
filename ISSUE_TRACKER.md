# Kodys Application – Issue Tracker & Fix Documentation

> **Date:** 21 March 2026  
> **Application:** Kodys Medical Desktop Application  
> **Stack:** Python 2.7.18, Django 1.11.29, SQLite3

---

## Status Legend

| Icon | Meaning |
|------|---------|
| ✅ | Fixed & Verified |
| 🔧 | Fix Applied (needs testing) |
| ⏳ | Pending |
| 🔬 | Requires device/hardware |

---

## Section A: 20 Reported Issues

### Issue #1 – OS Compatibility Issue
**Status:** ✅ Fixed  
**Root Cause:** Application was tightly coupled to Windows paths, registry, and COM ports.  
**Fix Applied:**
- Created Docker-based deployment (`Dockerfile`, `docker-compose.yml`) with `linux/amd64` platform emulation
- Changed all hardcoded `os.path` calls to use `os.path.join()` for cross-platform paths
- Added `REPORT_TO_PDF_PATH` conditional for Mac/Linux in `settings.py:222-226`

**Files Modified:** `Dockerfile`, `docker-compose.yml`, `settings.py`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-1.1 | Docker startup on Mac | `docker-compose up --build` | Server starts at port 5423 |
| TC-1.2 | Docker startup on Windows | `docker-compose up --build` | Server starts at port 5423 |
| TC-1.3 | Access via browser | Open `http://localhost:5423` | Login page loads with CSS |

---

### Issue #2 – Software Opening Problem (Too Slow)
**Status:** ✅ Fixed  
**Root Cause:** `MEDIA_URL` was hardcoded to `http://127.0.0.1:5423/site_media/` causing asset loading issues; large static asset bundles not cached.  
**Fix Applied:**
- Changed `MEDIA_URL` to relative path `/site_media/` in `settings.py:214`
- Works for localhost, ngrok, and cloudflare tunnels

**Files Modified:** `settings.py`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-2.1 | Local startup speed | Start app, time login page load | < 3 seconds |
| TC-2.2 | ngrok load speed | Load via ngrok URL | < 5 seconds |
| TC-2.3 | CSS/JS loads correctly | Inspect network tab | All assets return 200 |

---

### Issue #3 – CAN Test Report View (Too Slow)
**Status:** 🔧 Fix Applied  
**Root Cause:** ECG processing (filtering, QRS detection, HRV) was re-computed on every report view.  
**Fix Applied:**
- Created `process_can_test_data()` function in `app_api.py` to pre-calculate results at submission time
- Stored processed results in `TEST_RESULT` JSON field in `TX_MEDICALTESTREPORTS`
- Report view now reads pre-computed data instead of recalculating

**Files Modified:** `app_api.py`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-3.1 | Report view speed | Open a CAN report | Loads in < 2 seconds |
| TC-3.2 | Data correctness | Compare pre-computed vs on-the-fly results | Values match within 0.01 tolerance |
| TC-3.3 | Repeated views | View same report 5 times | Consistent load time |

---

### Issue #4 – CAN Test Report Generation Problem
**Status:** 🔧 Fix Applied  
**Root Cause:** Butterworth filter was incorrectly configured as low-pass instead of bandpass.  
**Fix Applied:**
- Corrected Butterworth filter to bandpass (5-15Hz) for ECG signal
- Added 50Hz notch filter for power line noise removal
- Fixed filter coefficients and order

**Files Modified:** `app_api.py`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-4.1 | Generate CAN report | Submit ECG data, generate report | Report generates without error |
| TC-4.2 | Signal quality | Check filtered ECG waveform | Clean, readable P-QRS-T morphology |
| TC-4.3 | Heart rate accuracy | Compare detected HR with known ECG data | Within ±5 BPM |

---

### Issue #5 – PDF Export Problem
**Status:** ⏳ Pending  
**Root Cause:** `wkhtmltopdf` path resolution fails on non-Windows platforms; `pdf2image` had Python 3 incompatibility.  
**Fix Applied (partial):**
- Downgraded `pdf2image` to 1.11.0 for Python 2.7 compatibility
- Added `subprocess32` backport
- `wkhtmltopdf` needs to be installed in Docker container

**Fix Needed:**
- Add `wkhtmltopdf` to `Dockerfile`
- Verify PDF generation end-to-end

**Files to Modify:** `Dockerfile`

```dockerfile
# Add to Dockerfile
RUN apt-get install -y wkhtmltopdf
```

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-5.1 | Export single report | Click PDF export on a report | PDF downloads correctly |
| TC-5.2 | PDF content | Open exported PDF | All data, graphs, gridlines visible |
| TC-5.3 | PDF on Mac/Linux | Export from Docker | PDF generates without path errors |

---

### Issue #6 – ECG Graph Report Problem (Plot Issue)
**Status:** 🔧 Fix Applied  
**Root Cause:** ECG SVG rendering used invisible gridline colors; matplotlib backend was misconfigured.  
**Fix Applied:**
- Changed gridline colors to visible pink/red in `canyscope_report_*.js.html`
- Added `.stroke_blue`, `.stroke_pink`, `.stroke_red` CSS classes in `kodysreports.css`
- Set matplotlib backend to `Agg` (non-GUI) for Docker compatibility

**Files Modified:** `canyscope_report_1_js.html`, `canyscope_report_2_js.html`, `kodysreports.css`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-6.1 | Gridline visibility | View CAN report in browser | Pink/red grid clearly visible |
| TC-6.2 | ECG trace | View ECG plot | Clean waveform on grid |
| TC-6.3 | Print preview | Ctrl+P on report page | Grid and ECG both visible in print |

---

### Issue #7 – Printing Problem in CAN Test
**Status:** 🔧 Fix Applied  
**Root Cause:** Report was not centered; print media queries missing.  
**Fix Applied:**
- Added `margin: 0 auto` to `.a4` container in `kodysreports.css`
- Fixed report centering in `report_view.html`
- Ensured SVG gridlines have explicit `stroke` colors (not transparent)

**Files Modified:** `kodysreports.css`, `report_view.html`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-7.1 | Print alignment | Print a CAN report | Centered on A4 page |
| TC-7.2 | Grid in print | Print preview | Gridlines visible |
| TC-7.3 | Multi-page print | Print report with multiple pages | All pages aligned correctly |

---

### Issue #8 – Poincare Plot & Histogram Correction
**Status:** 🔧 Fix Applied  
**Root Cause:** Poincare data (`RRn` vs `RRn+1`) and Histogram data (BPM bins) were not correctly computed.  
**Fix Applied:**
- Corrected Poincare scatter: `RRn = rr_intervals[:-1]`, `RRn_plus_1 = rr_intervals[1:]`
- Fixed Histogram binning to use proper BPM ranges
- Stored both in pre-computed `TEST_RESULT` JSON

**Files Modified:** `app_api.py`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-8.1 | Poincare scatter | View CAN report Poincare | Points cluster along identity line for normal ECG |
| TC-8.2 | Histogram bins | View CAN report histogram | Bell-shaped BPM distribution |
| TC-8.3 | Data consistency | Compare Poincare and histogram with R-R data | All data derived from same R-R intervals |

---

### Issue #9 – ECG Baseline Wandering Correction
**Status:** 🔧 Fix Applied  
**Root Cause:** `bwr.bwr()` filtering was not optimized for the signal characteristics.  
**Fix Applied:**
- Optimized `bwr.bwr` usage for baseline correction
- Applied high-pass filter cutoff at 0.5Hz to remove DC drift

**Files Modified:** `app_api.py`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-9.1 | Baseline stability | View a CAN ECG trace | No visible drift/wandering |
| TC-9.2 | Signal preservation | Compare raw vs filtered | P-QRS-T morphology preserved |

---

### Issue #10 – Pan Tompkins Algorithm Correction
**Status:** 🔧 Fix Applied  
**Root Cause:** `qrs_detector.py` had incorrect `filter_order`, `integration_window`, and `refractory_period`.  
**Fix Applied:**
- Increased `filter_order` to 2
- Adjusted `integration_window` and `refractory_period` for 250Hz sampling rate
- Improved peak detection robustness

**Files Modified:** `qrs_detector.py`, `app_api.py`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-10.1 | QRS detection accuracy | Run on known MIT-BIH ECG data | Sensitivity > 99% |
| TC-10.2 | Heart rate accuracy | Compare detected HR with known | Within ±3 BPM |
| TC-10.3 | Noisy signal handling | Run on noisy ECG | No false positives |

---

### Issue #11 – Diagnose Mode ECG Time Delay
**Status:** ⏳ Pending (Requires hardware)  
**Root Cause:** Real-time ECG streaming likely has buffering/serial port delay.  
**Fix Needed:**
- Optimize serial port buffer size and read frequency
- Reduce JavaScript rendering interval in real-time ECG view
- Consider WebSocket for lower-latency data push

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-11.1 | Real-time latency | Connect ECG device, measure delay | < 200ms latency |
| TC-11.2 | Buffer overflow | Run diagnose mode for 5 minutes | No data loss |

---

### Issue #12 – Need ECG Result Data in Excel
**Status:** 🔧 Fix Applied  
**Root Cause:** No export functionality existed.  
**Fix Applied:**
- Added `export_patients_excel()` function in `views.py:23`
- Uses `pandas` DataFrame to generate `.xlsx` with patient data and test summaries
- Added URL route for `/export/patients/excel/`

**Files Modified:** `views.py`, `urls.py`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-12.1 | Excel download | Click export button | `.xlsx` file downloads |
| TC-12.2 | Data completeness | Open Excel | All patients with correct fields |
| TC-12.3 | Special characters | Patient with Unicode name | Renders correctly in Excel |

---

### Issue #13 – DB Backup Option
**Status:** ⏳ Pending  
**Root Cause:** No backup view/API exists in the codebase.  
**Fix Needed:**
- Create `db_backup()` management command
- Create UI button in Settings page
- Copy `db.sqlite3` to timestamped backup location

**Files to Create/Modify:** `kodys/management/commands/db_backup.py`, `views.py`, `urls.py`

```python
# Management command: kodys/management/commands/db_backup.py
import shutil, os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        backup_path = db_path + '.backup_%s' % datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copy2(db_path, backup_path)
        self.stdout.write('Backup created: %s' % backup_path)
```

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-13.1 | Backup creation | Click backup button | `.sqlite3.backup_*` file created |
| TC-13.2 | Backup restore | Replace DB with backup | App works with old data |
| TC-13.3 | Backup size | Compare backup with original | Same file size |

---

### Issue #14 – Need Descriptive Interpretation for All Reports
**Status:** ⏳ Pending  
**Root Cause:** Interpretations stored in `MA_MEDICALTESTMASTERINTERPERTATION.RANGES` JSON are range-based only; no clinical text.  
**Fix Needed:**
- Add `DESCRIPTION` text field to `MA_MEDICALTESTMASTERINTERPERTATION` model
- Populate clinical interpretations for each test range
- Display in report template

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-14.1 | Normal interpretation | View report with normal values | "Normal" text with clinical description |
| TC-14.2 | Abnormal interpretation | View report with abnormal values | Warning text with recommended actions |

---

### Issue #15 – Machine Power Off & USB Detection (VPT/VPT Ultra)
**Status:** 🔬 Requires Hardware  
**Root Cause:** No device disconnect detection implemented in the serial/USB communication layer.  
**Fix Needed:**
- Add USB device enumeration check (via `pyserial` or `pyusb`)
- Add periodic heartbeat check during test mode
- Show alert modal when device disconnects

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-15.1 | USB disconnect | Unplug device during test | Alert appears within 3 seconds |
| TC-15.2 | Power off detection | Turn off device | Alert with "Device powered off" message |
| TC-15.3 | Reconnection | Replug device | App auto-reconnects or prompts user |

---

### Issue #16 – ABI & TBI Calculation Correction
**Status:** ⏳ Pending  
**Root Cause:** ABI calculation at `app_api.py:3039` uses hardcoded indices (`tx_test_entries[20]`, `tx_test_entries[22]`) which may not map correctly to ankle/brachial pressure fields.  
**Current Code (line 3039):**
```python
right_abi = round(float(float(tx_test_entries[20].KEY_VALUE)/float(tx_test_entries[22].KEY_VALUE)), 2)
```
**Issue:** Division by zero if brachial pressure is 0; hardcoded indices are fragile.

**Fix Needed:**
- Use `KEY_CODE` lookup instead of positional index
- Add zero-division protection
- Verify ABI formula: `ABI = Ankle Systolic / Higher Brachial Systolic`
- Add TBI calculation: `TBI = Toe Systolic / Brachial Systolic`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-16.1 | Normal ABI | Ankle=120, Brachial=110 | ABI = 1.09 (Normal) |
| TC-16.2 | Low ABI | Ankle=70, Brachial=130 | ABI = 0.54 (Severe) |
| TC-16.3 | Zero brachial | Ankle=120, Brachial=0 | "No Data" (no crash) |
| TC-16.4 | TBI calculation | Toe=80, Brachial=120 | TBI = 0.67 |

---

### Issue #17 – VPT & HCP Graphical Report Change
**Status:** ⏳ Pending  
**Root Cause:** Graphical templates need visual updates per client requirements.  
**Fix Needed:** Template changes to VPT/HCP report HTML files based on client specifications.

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-17.1 | VPT report layout | Generate VPT report | Matches new design spec |
| TC-17.2 | HCP report layout | Generate HCP report | Matches new design spec |

---

### Issue #18 – License Update Option (Product Addition)
**Status:** ⏳ Pending  
**Root Cause:** Current license system doesn't support adding products post-initial-setup.  
**Fix Needed:**
- Add "Update License" button in App Configuration
- Parse new license file to add/extend product permissions
- Update `MA_APPLICATION` or a new license table

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-18.1 | Upload new license | Upload updated license file | New products appear |
| TC-18.2 | Invalid license | Upload corrupt license file | Error message displayed |

---

### Issue #19 – Patient Name Search Problem
**Status:** ⏳ Pending (code identified, fix ready)  
**Root Cause:** Search at `app_api.py:1771` only filters by `NAME` field, ignoring `LAST_NAME` and `SUR_NAME`:
```python
patients = TX_PATIENTS.objects.filter(NAME__icontains=search_key, DATAMODE="A")
```
**Fix Needed:** Use `Q` objects to search across all name fields:
```python
patients = TX_PATIENTS.objects.filter(
    Q(NAME__icontains=search_key) |
    Q(LAST_NAME__icontains=search_key) |
    Q(SUR_NAME__icontains=search_key) |
    Q(FRIENDLY_UID__icontains=search_key),
    DATAMODE="A"
).order_by('pk')
```

**Files to Modify:** `app_api.py:1771`

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-19.1 | Search first name | Search "John" | John Doe appears |
| TC-19.2 | Search last name | Search "Doe" | John Doe appears |
| TC-19.3 | Search patient ID | Search "100100" | John Doe appears |
| TC-19.4 | Partial search | Search "Jo" | All patients with "Jo" in any name |
| TC-19.5 | Case insensitive | Search "john" | John Doe appears |

---

### Issue #20 – Email Configuration Problem
**Status:** ⏳ Pending (code identified)  
**Root Cause:** `email_report()` at `app_api.py:4747` reads SMTP settings from `MA_APPLICATION_SETTINGS` rows (SET-01 to SET-05). If these rows don't exist, it falls back to `settings.py` defaults which may have stale credentials.  
**Fix Needed:**
- Ensure Settings page has proper SMTP configuration form
- Add validation before sending (check connectivity)
- Handle `urllib2.urlopen` timeout gracefully (line 4755)

**Test Cases:**
| # | Test | Steps | Expected |
|---|------|-------|----------|
| TC-20.1 | Valid SMTP config | Configure Gmail SMTP, send test | Email delivered |
| TC-20.2 | Invalid SMTP | Wrong password | Error message (no crash) |
| TC-20.3 | No internet | Disconnect network, send email | Graceful error message |

---

## Section B: 7 Additional Requirements

### Requirement #1 – Add 2 More BP Measurements
**Status:** ⏳ Pending  
**Work Needed:**
- Add 2 new BP fields to `MA_MEDICALTESTFIELDS` and `TX_MEDICALTESTENTRIES`
- Update form templates to include additional input fields
- Update report templates to display all BP measurements

---

### Requirement #2 – ECG Grid Background (Red Colour)
**Status:** ✅ Fixed  
**Fix Applied:**
- Added `.stroke_pink` (rgba(255,182,193,0.6)) and `.stroke_red` (rgba(255,0,0,0.3)) to `kodysreports.css`
- Applied to grid `<line>` elements in `canyscope_report_*.js.html`

---

### Requirement #3 – ECG Baseline Wandering Removal (Real-time)
**Status:** 🔧 Fix Applied  
**Fix Applied:**
- Implemented high-pass Butterworth filter at 0.5Hz cutoff in `app_api.py`
- Uses `scipy.signal.butter` with `btype='highpass'`

---

### Requirement #4 – ECG Power Line Interference Removal (Real-time)
**Status:** 🔧 Fix Applied  
**Fix Applied:**
- Implemented 50Hz notch filter using `scipy.signal.iirnotch` in `app_api.py`
- Quality factor Q=30 for narrow stop band around 50Hz

---

### Requirement #5 – Working Code for Histogram Plotting
**Status:** 🔧 Fix Applied  
**Fix Applied:** Histogram BPM binning corrected in `process_can_test_data()`.

---

### Requirement #6 – Working Code for Poincare Plotting
**Status:** 🔧 Fix Applied  
**Fix Applied:** Poincare scatter corrected: `RRn` vs `RRn+1` from consecutive R-R intervals.

---

### Requirement #7 – QT Interval Finding in ECG
**Status:** ⏳ Pending (research required)  
**Work Needed:**
- QT interval = Q-onset to T-end
- Algorithm: detect Q-onset (first downward deflection before R-peak) and T-end (return to baseline after T-wave)
- Libraries: `biosppy.signals.ecg`, `neurokit2` (Python 3 only)
- For Python 2.7: Custom implementation needed using `scipy.signal.find_peaks`

---

## Summary Dashboard

| Category | Total | ✅ Fixed | 🔧 Applied | ⏳ Pending | 🔬 Hardware |
|----------|-------|---------|------------|-----------|-------------|
| **20 Issues** | 20 | 3 | 7 | 8 | 2 |
| **7 Requirements** | 7 | 1 | 4 | 2 | 0 |
| **Overall** | **27** | **4** | **11** | **10** | **2** |

### Priority for Remaining Fixes

| Priority | Issue | Effort |
|----------|-------|--------|
| 🔴 High | #19 Patient Name Search | 30 min |
| 🔴 High | #5 PDF Export | 1 hour |
| 🔴 High | #16 ABI/TBI Calculation | 2 hours |
| 🟡 Medium | #13 DB Backup | 1 hour |
| 🟡 Medium | #20 Email Config | 1 hour |
| 🟡 Medium | #14 Descriptive Interpretation | 2 hours |
| 🟡 Medium | #18 License Update | 2 hours |
| 🟢 Low | #11 ECG Time Delay | Hardware needed |
| 🟢 Low | #15 USB Detection | Hardware needed |
| 🟢 Low | #17 VPT/HCP Report Design | Client spec needed |
| 🟢 Low | Req #1 BP Measurements | 2 hours |
| 🟢 Low | Req #7 QT Interval | Research needed |
