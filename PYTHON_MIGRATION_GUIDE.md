# Python 2.7 → 3.12 Migration – Complete Analysis

> **Date:** 21 March 2026  
> **Current:** Python 2.7.18 + Django 1.11.29  
> **Target:** Python 3.12 + Django 4.2 LTS

---

## Executive Summary

> [!IMPORTANT]
> Migration **IS possible** but requires **significant effort**. It is NOT a simple version bump — it impacts every `.py` file in the project. Estimated effort: **3–4 weeks** for a developer familiar with the codebase.

### Recommended Target Versions

| Component | Current | Recommended | Why Not Latest? |
|-----------|---------|-------------|-----------------|
| **Python** | 2.7.18 | **3.12** | 3.14 is too new; library support still maturing |
| **Django** | 1.11.29 | **4.2 LTS** | Long-term support until April 2026; stable upgrade path |
| **NumPy** | 1.16.6 | 1.26.x | Last to support Python 3.12 stably |
| **SciPy** | 1.2.3 | 1.12.x | Modern signal processing APIs |
| **Pandas** | 0.24.2 | 2.1.x | Major API improvements |
| **Matplotlib** | 2.2.5 | 3.8.x | Better SVG/PDF rendering |

---

## Codebase Impact Analysis

### 1. Python Syntax Changes (BREAKING)

| Change | Count | Example | Fix |
|--------|-------|---------|-----|
| `except Exception, e:` | **65+** | `except Exception, e:` | `except Exception as e:` |
| `__unicode__` methods | **30** | `def __unicode__(self):` | Rename to `__str__` |
| `sys.exc_traceback` | **130+** | `sys.exc_traceback.tb_lineno` | `sys.exc_info()[2].tb_lineno` |
| `print` statements | **5** | `print 'message'` | `print('message')` |
| `urllib2` import | **1** | `import urllib2` | `from urllib import request` |
| String formatting `%` | **100+** | `"%s %s" % (a, b)` | Works in Py3, but `f""` preferred |
| `dict.has_key()` | **0** | None found | N/A |
| `unicode()` calls | ~10 | `unicode(x)` | `str(x)` |

**Automated fix available:** Python's built-in `2to3` tool can fix ~80% of these automatically:
```bash
2to3 -w app/appsource/kodys/
```

### 2. Django Migration (CRITICAL)

Django 1.11 → 4.2 is a **4-version jump** with many breaking changes:

| Django Change | Impact | Files Affected |
|---------------|--------|----------------|
| `url()` → `path()` / `re_path()` | URL routing rewrite | `urls.py` |
| `django.core.urlresolvers` removed | Import path change | `app_api.py` |
| `request.user.is_authenticated()` → `.is_authenticated` | Remove `()` | `context_processors.py`, `views.py` |
| `on_delete` required on ForeignKey | Must add to all 40+ ForeignKeys | `models.py` |
| `{% load staticfiles %}` removed | Template tag change | All templates |
| Middleware class changes | `MIDDLEWARE_CLASSES` → `MIDDLEWARE` | `settings.py` |
| `render_to_response` removed | Use `render()` | `views.py` |

### 3. Library Compatibility

| Library | Current (Py2.7) | Python 3.12 Version | Migration Notes |
|---------|-----------------|---------------------|-----------------|
| `biosppy` | 0.6.1 | 2.2.1 | API mostly compatible |
| `Django` | 1.11.29 | 4.2.x | **Major rewrite** (see above) |
| `jsonfield` | 2.0.2 | 3.1.x | Use Django's built-in `JSONField` |
| `numpy` | 1.16.6 | 1.26.x | Compatible, minor deprecations |
| `pandas` | 0.24.2 | 2.1.x | `.append()` removed, use `pd.concat()` |
| `scipy` | 1.2.3 | 1.12.x | Compatible |
| `matplotlib` | 2.2.5 | 3.8.x | Some API renames |
| `heartpy` | 1.2.7 | 1.2.7 | Should work |
| `pyhrv` | 0.4.1 | 0.4.1 | **May need patching** for Py3 |
| `opencv-python` | 4.2.0.32 | 4.9.x | Compatible |
| `Pillow` | 6.2.2 | 10.x | Compatible |
| `pdf2image` | 1.11.0 | 1.17.x | Compatible |
| `cryptography` | 2.9.2 | 42.x | **Major API changes** |
| `shortuuid` | 0.5.0 | 1.0.x | Compatible |
| `spectrum` | 0.7.5 | 0.8.x | Compatible |
| `scikit-learn` | 0.20.4 | 1.4.x | **API changes**, check model usage |
| `nolds` | 0.5.2 | 0.6.x | Compatible |
| `pathlib` | 1.0.1 | Built-in | Remove from requirements |
| `subprocess32` | 3.5.4 | Built-in | Remove from requirements |

### 4. Desktop App (PyQt4 + CEF)

| Component | Current | Python 3 Equivalent | Effort |
|-----------|---------|---------------------|--------|
| `PyQt4` | 4.x | **PyQt6** or **PySide6** | **Complete rewrite** of UI code |
| `CEF` (cefpython3) | 3.x | **Not available for Py3** | Replace with `PyWebView` or `Electron` |

> [!CAUTION]
> The desktop launcher (`Kodys Foot Clinik.exe`) uses `cefpython3` which has **NO Python 3 support**. This is the single biggest blocker for migration. The entire desktop wrapper must be replaced.

---

## Migration Strategy

### Option A: Full Migration (Recommended)

**Timeline: 3–4 weeks**

```
Week 1: Automated syntax fixes + Django upgrade
Week 2: Library upgrades + test framework
Week 3: Desktop app replacement (CEF → PyWebView)
Week 4: Testing + validation
```

#### Step-by-Step Plan

| Step | Task | Tool/Method | Risk |
|------|------|-------------|------|
| 1 | Run `2to3 -w` on all `.py` files | `2to3` tool | Low |
| 2 | Fix `except Exception, e:` → `except Exception as e:` | Find & replace | Low |
| 3 | Fix `__unicode__` → `__str__` | Find & replace | Low |
| 4 | Fix `sys.exc_traceback` → `sys.exc_info()[2]` | Find & replace | Low |
| 5 | Replace `urllib2` → `urllib.request` | Manual | Low |
| 6 | Upgrade Django 1.11 → 2.2 → 3.2 → 4.2 | Incremental | **High** |
| 7 | Add `on_delete=models.CASCADE` to all ForeignKeys | Manual (40+ fields) | Medium |
| 8 | Fix `request.user.is_authenticated()` → `.is_authenticated` | Find & replace | Low |
| 9 | Update `urls.py` patterns | Manual | Medium |
| 10 | Upgrade all pip dependencies | `requirements.txt` | Medium |
| 11 | Replace `cefpython3` desktop wrapper | Rewrite to `PyWebView` | **High** |
| 12 | Run full test suite | Manual + automated | **High** |

### Option B: Docker-Only (No Desktop App)

**Timeline: 1–2 weeks**

Skip the CEF/PyQt4 problem entirely by delivering as a **web-only application** via Docker. Clients access it from a browser on any device.

| Pros | Cons |
|------|------|
| No CEF/PyQt4 rewrite needed | Requires server/Docker on client network |
| Cross-platform automatically | Client needs basic Docker setup |
| Much faster to deliver | Loses "desktop app" feel |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| ECG algorithm output changes | 🔴 Critical | Side-by-side validation against Py2.7 results |
| Django ORM query behavior changes | 🟡 Medium | Comprehensive database query testing |
| `pyhrv` incompatibility | 🟡 Medium | Fork and patch if needed |
| Desktop app (CEF) replacement | 🔴 Critical | Consider Docker-only delivery |
| Template rendering differences | 🟢 Low | Visual comparison testing |

---

## New requirements.txt (Python 3.12)

```txt
# Core
Django==4.2.11
jsonfield==3.1.0

# Data Science
numpy==1.26.4
scipy==1.12.0
pandas==2.1.4
matplotlib==3.8.3
scikit-learn==1.4.0

# Medical / ECG
biosppy==2.2.1
heartpy==1.2.7
pyhrv==0.4.1
nolds==0.6.1
spectrum==0.8.1

# Image & PDF
opencv-python==4.9.0.80
Pillow==10.2.0
pdf2image==1.17.0

# Utilities
cryptography==42.0.2
shortuuid==1.0.13
python-dateutil==2.8.2
pytz==2024.1
six==1.16.0
xlrd==2.0.1
```

---

## Recommendation

> [!IMPORTANT]
> **Go with Python 3.12 + Django 4.2 LTS** — this is the sweet spot for stability and modern library support. Python 3.14 is too bleeding-edge.

### Suggested Approach

1. **Phase 1 (Now):** Continue with Python 2.7 Docker deployment for immediate client testing
2. **Phase 2 (Next sprint):** Create a `python3-migration` branch and apply the automated fixes
3. **Phase 3:** Choose between **Option A** (full migration with desktop) or **Option B** (Docker-only)
4. **Phase 4:** Side-by-side ECG validation — run the same test data through both versions and compare results

> [!WARNING]
> **Do NOT attempt a direct in-place upgrade on the main branch.** Always work in a separate branch with the Py2.7 version as the reference baseline for medical algorithm validation.
