# Python 2.7 → 3.12 Migration – Effort Estimation & Test Package

> **Project:** Kodys Medical Application  
> **Date:** 22 March 2026  
> **Current Stack:** Python 2.7.18 | Django 1.11.29 | SQLite3  
> **Target Stack:** Python 3.12 | Django 4.2 LTS | SQLite3

---

## 1. Codebase Summary

| Metric | Count |
|--------|-------|
| Python files | **20** |
| Total Python lines | **11,415** |
| HTML templates | **72** |
| URL patterns | **103** |
| Database models | **30** |
| Existing tests | **0** (empty `tests.py`) |

### Key Files by Size

| File | Lines | Migration Impact |
|------|-------|-----------------|
| `app_api.py` | 7,674 | 🔴 Heavy – exception handling, urllib2, string formatting |
| `views.py` | 1,429 | 🔴 Heavy – exception handling, sys.exc_traceback |
| `models.py` | 611 | 🟡 Medium – ForeignKeys, __unicode__ |
| `qrs_detector.py` | 266 | 🟢 Low – pure math/scipy |
| `bwr.py` | 146 | 🟢 Low – pure numpy |
| `urls.py` | 125 | 🟡 Medium – url() → path()/re_path() |
| `app_logger.py` | 88 | 🟡 Medium – print statements |
| `settings.py` | 227 | 🟢 Low – MIDDLEWARE already correct |

---

## 2. Exact Code Changes Required

### 2.1 Python 2 → 3 Syntax (Auto-fixable ~80%)

| Pattern | Occurrences | Fix | Auto? |
|---------|------------|-----|-------|
| `except Exception, e:` | **230+** | `except Exception as e:` | ✅ `2to3` |
| `sys.exc_traceback.tb_lineno` | **230+** | `sys.exc_info()[2].tb_lineno` | ✅ sed/replace |
| `__unicode__(self)` | **30** | `__str__(self)` | ✅ sed/replace |
| `import urllib2` | **1** | `from urllib import request, parse` | ❌ Manual |
| `urllib2.urlopen` / `urllib2.Request` | **~5** | `request.urlopen` / `request.Request` | ❌ Manual |
| `print` statements (as keyword) | **5** | `print()` function | ✅ `2to3` |
| `unicode()` calls | **~10** | `str()` | ✅ `2to3` |
| `% string formatting` | **200+** | Works in Py3 (no change needed) | N/A |

**Estimated time:** 2–3 hours (mostly automated)

### 2.2 Django 1.11 → 4.2 (Manual work)

| Change | Occurrences | Effort |
|--------|------------|--------|
| `ForeignKey(Model)` → `ForeignKey(Model, on_delete=models.CASCADE)` | **40** | 2 hours |
| `url(r'^pattern$', view)` → `re_path(r'^pattern$', view)` | **103** | 3 hours |
| `from django.conf.urls import url` → `from django.urls import re_path` | **1** | 5 min |
| `render_to_response` → `render` (if found) | Check needed | 30 min |
| `jsonfield` → Django built-in `JSONField` | **2 models** | 30 min |
| Remove `pathlib` from requirements (built into Py3) | **1 line** | 1 min |
| Remove `subprocess32` from requirements (built into Py3) | **1 line** | 1 min |

**Estimated time:** 6–8 hours

### 2.3 Library Upgrades

| Library | Current → Target | Breaking Changes | Effort |
|---------|-----------------|------------------|--------|
| Django | 1.11 → 4.2 | Major (see 2.2) | Included above |
| numpy | 1.16 → 1.26 | Minor deprecations | 1 hour |
| scipy | 1.2 → 1.12 | API compatible | 30 min |
| pandas | 0.24 → 2.1 | `.append()` removed, use `pd.concat()` | 1 hour |
| matplotlib | 2.2 → 3.8 | Some API renames | 1 hour |
| cryptography | 2.9 → 42.x | Major API changes | 2 hours |
| scikit-learn | 0.20 → 1.4 | Model API changes | 1 hour |
| biosppy | 0.6 → 2.2 | Mostly compatible | 30 min |
| pyhrv | 0.4.1 → 0.4.1 | May need patching for Py3 | 2 hours |
| opencv-python | 4.2 → 4.9 | Compatible | 15 min |
| Pillow | 6.2 → 10.x | Compatible | 15 min |
| heartpy | 1.2 → 1.2 | Should work | 15 min |

**Estimated time:** 8–10 hours

### 2.4 Desktop App (CEF/PyQt4)

| Component | Status | Effort |
|-----------|--------|--------|
| `cefpython3` | ❌ No Python 3 support | Replace with `pywebview` (3 days) |
| `PyQt4` | ❌ No Python 3 support | Replace with browser-based launcher (1 day) |

**Estimated time:** 3–4 days (OR skip entirely with Docker-only delivery)

---

## 3. Total Effort Estimation

### Option A: Full Migration (Desktop + Server)

| Phase | Tasks | Duration | Developer Days |
|-------|-------|----------|----------------|
| **Phase 1: Syntax Conversion** | Python 2→3 automated fixes, manual urllib2, print | 1 day | 1 |
| **Phase 2: Django Upgrade** | ForeignKey on_delete, URL patterns, settings | 2 days | 2 |
| **Phase 3: Library Upgrades** | Update all 20 libraries, fix breaking changes | 2 days | 2 |
| **Phase 4: Desktop App** | Replace CEF/PyQt4 with pywebview or browser | 3 days | 3 |
| **Phase 5: Test Suite** | Write and run full test package (see Section 4) | 3 days | 3 |
| **Phase 6: ECG Validation** | Side-by-side algorithm comparison Py2 vs Py3 | 2 days | 2 |
| **Phase 7: Docker + CI/CD** | Update Dockerfile, pipeline for Py3 | 1 day | 1 |
| **TOTAL** | | **14 working days** | **14** |

### Option B: Server/Docker Only (No Desktop App)

| Phase | Tasks | Duration | Developer Days |
|-------|-------|----------|----------------|
| Phase 1: Syntax Conversion | Same as above | 1 day | 1 |
| Phase 2: Django Upgrade | Same as above | 2 days | 2 |
| Phase 3: Library Upgrades | Same as above | 2 days | 2 |
| Phase 4: Test Suite | Write and run full test package | 3 days | 3 |
| Phase 5: ECG Validation | Side-by-side comparison | 1 day | 1 |
| Phase 6: Docker + CI/CD | Update Dockerfile, pipeline | 1 day | 1 |
| **TOTAL** | | **10 working days** | **10** |

---

## 4. Test Package Design

> **Current test coverage: ZERO.** The `tests.py` file is empty. A complete test suite must be built from scratch.

### 4.1 Test Structure

```
app/appsource/kodys/
├── tests/
│   ├── __init__.py
│   ├── test_models.py          # Model validation tests
│   ├── test_views.py           # View/URL response tests
│   ├── test_api.py             # API logic tests
│   ├── test_ecg.py             # ECG algorithm tests  
│   ├── test_patient_search.py  # Patient search tests
│   ├── test_reports.py         # Report generation tests
│   ├── test_auth.py            # Authentication tests
│   └── test_migration.py      # Data integrity tests
```

### 4.2 Test Cases by Module

#### Module 1: Authentication (`test_auth.py`) – 6 tests

| # | Test | Method | Expected |
|---|------|--------|----------|
| 1 | Login with valid credentials | POST `/signin/` | Redirect to home |
| 2 | Login with invalid password | POST `/signin/` | Error message |
| 3 | Access home without login | GET `/` | Redirect to signin |
| 4 | Signout | GET `/signout/` | Redirect to signin |
| 5 | Admin panel access | GET `/admin/` | Admin login page (200) |
| 6 | Session persistence | Login → navigate pages | Session maintained |

#### Module 2: Patient Management (`test_patient_search.py`) – 10 tests

| # | Test | Method | Expected |
|---|------|--------|----------|
| 1 | Add patient | POST `/patient/add/` | Patient created, redirect |
| 2 | Edit patient | POST `/patient/edit/{uid}/` | Patient updated |
| 3 | Delete patient | GET `/patient/delete/{uid}/` | Patient marked inactive |
| 4 | Search by first name | GET `/patient/search/John/` | Results with "John" |
| 5 | Search by last name | GET `/patient/search/Doe/` | Results with "Doe" |
| 6 | Search by patient ID | GET `/patient/search/100100/` | Matching patient |
| 7 | Search case insensitive | GET `/patient/search/john/` | Same as "John" |
| 8 | Search empty result | GET `/patient/search/ZZZZZ/` | Empty list, no error |
| 9 | Patient list view | GET `/patients/` | 200, patient table |
| 10 | Export patients Excel | GET `/export/patients/` | .xlsx file download |

#### Module 3: Medical Tests (`test_api.py`) – 12 tests

| # | Test | Method | Expected |
|---|------|--------|----------|
| 1 | Doppler test entry | POST `/APP-01/{uid}/...` | Test created |
| 2 | VPT test entry | POST `/APP-02/{uid}/...` | Test created |
| 3 | VPT Ultra test entry | POST `/APP-03/{uid}/...` | Test created |
| 4 | Thermocool test entry | POST `/APP-04/{uid}/...` | Test created |
| 5 | CAN test entry | POST `/APP-07/{uid}/...` | Test created |
| 6 | Report generation | GET `/report/view/{code}/` | Report HTML (200) |
| 7 | CAN report generation | GET `/report/view/canyscope/{code}/` | CAN report (200) |
| 8 | ABI calculation | API call with ankle=120,brachial=110 | ABI=1.09 |
| 9 | ABI zero division | API call with brachial=0 | Graceful "N/A" |
| 10 | Email report | POST `/email/report/` | Email sent or error |
| 11 | DB backup | GET `/database/backup/` | Backup file created |
| 12 | Doctor CRUD | Add/edit/delete doctor | Doctor lifecycle works |

#### Module 4: ECG Algorithms (`test_ecg.py`) – 8 tests ⚠️ CRITICAL

| # | Test | Method | Expected |
|---|------|--------|----------|
| 1 | Bandpass filter (5-15Hz) | Feed known signal | Filtered output matches expected |
| 2 | 50Hz notch filter | Feed 50Hz sine wave | Attenuation > 30dB |
| 3 | Baseline wander removal | Feed DC drift + ECG | Clean baseline, P-QRS-T preserved |
| 4 | QRS detection accuracy | Feed MIT-BIH sample | Sensitivity > 99% |
| 5 | Heart rate calculation | Feed 60 BPM signal | HR = 60 ± 3 BPM |
| 6 | R-R interval extraction | Feed known ECG | R-R intervals match reference |
| 7 | Poincare plot data | Feed R-R intervals | Correct RRn vs RRn+1 pairs |
| 8 | Histogram BPM bins | Feed heart rates | Correct frequency distribution |

#### Module 5: Models (`test_models.py`) – 8 tests

| # | Test | Method | Expected |
|---|------|--------|----------|
| 1 | Create MA_APPLICATION | Model.objects.create() | Row saved |
| 2 | Create TX_PATIENTS | Model with all required fields | Patient saved |
| 3 | ForeignKey cascade | Delete parent | Children deleted |
| 4 | __str__ output | str(model_instance) | Human-readable string |
| 5 | JSONField read/write | Store/retrieve JSON | Data integrity maintained |
| 6 | Date fields | Auto-set created/updated | Timestamps set correctly |
| 7 | UID generation | Create instance | Unique UID assigned |
| 8 | DATAMODE filtering | Filter DATAMODE="A" | Only active records |

#### Module 6: Views & URLs (`test_views.py`) – 10 tests

| # | Test | Method | Expected |
|---|------|--------|----------|
| 1 | Home page | GET `/` | 200 / 302 (login required) |
| 2 | About page | GET `/about/` | 200 |
| 3 | Reports page | GET `/reports/` | 200, report listing |
| 4 | Hospital profile | GET `/hospital/profile/` | 200, profile form |
| 5 | App configuration | GET `/app/configuration/` | 200, settings page |
| 6 | Manuals page | GET `/manuals/` | 200, manuals listing |
| 7 | Static files served | GET `/site_media/...` | 200, file served |
| 8 | 404 handling | GET `/nonexistent/` | 404 page |
| 9 | Customer support | GET `/customer/support/` | 200 |
| 10 | All URL patterns resolve | Loop all urlpatterns | No resolution errors |

### 4.3 Test Execution Commands

```bash
# Run ALL tests
python manage.py test kodys.tests -v 2

# Run specific module
python manage.py test kodys.tests.test_auth -v 2
python manage.py test kodys.tests.test_ecg -v 2
python manage.py test kodys.tests.test_patient_search -v 2

# Run with coverage report
pip install coverage
coverage run manage.py test kodys.tests -v 2
coverage report --include="kodys/*"
coverage html  # generates htmlcov/index.html
```

### 4.4 CI/CD Integration

Add to `.github/workflows/build-release.yml`:
```yaml
test:
  name: 🧪 Run Test Suite
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Build & Test
      run: |
        docker build -t kodys-test .
        docker run kodys-test python manage.py test kodys.tests -v 2
```

---

## 5. Migration Workflow (Step-by-Step)

```
Step 1  │ Create 'python3-migration' branch
Step 2  │ Run `2to3 -w` on all .py files
Step 3  │ Fix remaining Python 2 → 3 issues manually
Step 4  │ Update Django: 1.11 → 2.2 → 3.2 → 4.2 (incremental)
Step 5  │ Add on_delete to all 40 ForeignKeys
Step 6  │ Convert urls.py: url() → re_path()
Step 7  │ Update requirements.txt with Python 3 versions
Step 8  │ Update Dockerfile: python:2.7-slim → python:3.12-slim
Step 9  │ Write test package (54 tests)
Step 10 │ Run test suite, fix failures
Step 11 │ ECG side-by-side validation (Py2 vs Py3 results)
Step 12 │ Client UAT (User Acceptance Testing)
Step 13 │ Merge to main, tag release
```

---

## 6. Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| ECG results differ between Py2/Py3 | Medium | 🔴 Critical | Side-by-side validation with known data |
| pyhrv incompatible with Py3 | High | 🟡 Medium | Fork and patch, or replace with biosppy |
| Django migration breaks DB | Low | 🔴 Critical | Full DB backup before migration |
| cryptography API breaks | Medium | 🟡 Medium | Rewrite encryption functions |
| Template rendering changes | Low | 🟢 Low | Visual comparison testing |
| CEF replacement behaviour | High | 🟡 Medium | Docker-only mode as fallback |

---

## 7. Summary

| Metric | Value |
|--------|-------|
| **Total code changes** | ~850 lines modified |
| **Auto-fixable** | ~650 lines (76%) |
| **Manual work** | ~200 lines (24%) |
| **New tests to write** | 54 test cases |
| **Duration (with desktop)** | 14 working days |
| **Duration (Docker only)** | 10 working days |
| **Risk level** | Medium (with proper validation) |
