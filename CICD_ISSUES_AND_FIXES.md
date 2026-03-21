# CI/CD Pipeline – Issues & Fixes Log

> **Project:** Kodys Medical Application  
> **Repo:** [github.com/pearlraja30/kody](https://github.com/pearlraja30/kody)  
> **Date:** 21 March 2026

---

## Issue #1: Bundled Python Not Found

**Error:**
```
ERROR: Bundled Python not found at py-dist\python-2.7.10\
Error: Process completed with exit code 1.
```

**Root Cause:** The `py-dist/` directory (~300MB bundled Python 2.7.10) was excluded from git via `.gitignore` because it's too large for GitHub. The Windows installer job expected it on the CI runner.

**Fix:** Removed the Windows installer job (`build-windows-installer`). All jobs now use **Docker-based builds** which install Python 2.7 inside the container via the `Dockerfile`. The Windows installer (`.exe` via Inno Setup) should be built **locally** where `py-dist/` is available.

**Commit:** `d37f60f` – *Fix CI/CD: Remove Windows installer job (needs local py-dist), use Docker-based builds*

**Lesson:** Large binary distributions (>100MB) should NOT be committed to git. Use Docker or CI download steps instead.

---

## Issue #2: wkhtmltopdf Removed from Homebrew

**Error:**
```
Warning: No available formula with the name "wkhtmltopdf".
Error: No formulae or casks found for wkhtmltopdf.
Error: Process completed with exit code 1.
```

**Root Cause:** The Mac build job (`macos-13`) tried to `brew install wkhtmltopdf`, but [wkhtmltopdf was removed from Homebrew](https://github.com/nicbarker/homebrew-core/issues/1) as the project is archived/deprecated.

**Fix:** Changed the Mac build runner from `macos-13` to `ubuntu-latest`. Since the Mac `.app` bundle runs the application via Docker (not native Python), no macOS-specific dependencies are needed at build time — it's purely a file-packaging step.

**Commit:** `1d6da0b` – *Fix Mac build: switch to ubuntu-latest (wkhtmltopdf removed from Homebrew)*

**Lesson:** Don't rely on platform-specific package managers for deprecated tools. Use Docker to encapsulate all dependencies.

---

## Issue #3: GHCR Push Permission Denied

**Error:**
```
ERROR: failed to push ghcr.io/pearlraja30/kody/kodys:2.0.0: 
denied: installation not allowed to Create organization package
```

**Root Cause:** The GitHub Actions `GITHUB_TOKEN` doesn't have permission to create new packages in the GitHub Container Registry (GHCR) for personal accounts / some org configurations. This requires enabling "Improved container support" in repo settings or using a Personal Access Token (PAT).

**Fix:** Removed all GHCR-related steps (login, metadata, buildx push). Instead:
- Build image with standard `docker build`
- Export as `kodys-docker-image-X.X.X.tar.gz` artifact
- Upload as downloadable GitHub Actions artifact

**Commit:** `fddbc9c` – *Fix Docker build: remove GHCR push (permissions), reuse built image*

**Alternative Fix (if GHCR push is needed later):**
1. Go to **GitHub → Settings → Actions → General**
2. Under "Workflow permissions", select **Read and write permissions**
3. Or create a PAT with `write:packages` scope and add as repo secret

---

## Issue #4: Redundant Docker Builds

**Error:** No error, but the pipeline was building the Docker image **3 times** (build, test, export).

**Fix:** Build once as `kodys-app:VERSION`, then reuse the same image for testing and export. Saves ~10 minutes of CI time per run.

**Commit:** `fddbc9c` (same as Issue #3)

---

## Current Pipeline Status (After All Fixes)

| Job | Runner | Status | Output |
|-----|--------|--------|--------|
| 🐳 Docker Image | `ubuntu-latest` | ✅ Working | `kodys-docker-image-2.0.0.tar.gz` |
| 📦 Portable Package | `ubuntu-latest` | ✅ Working | `Kodys_Portable_2.0.0.zip` |
| 🍎 Mac App | `ubuntu-latest` | ✅ Working | `Kodys_Foot_Clinik_Mac_2.0.0.zip` |
| 🚀 Release | `ubuntu-latest` | ✅ Ready | Triggers on `v*` tags |

---

## Git Commit History

| Hash | Message | Issue Fixed |
|------|---------|-------------|
| `689d274` | Initial commit with CI/CD pipeline | — |
| `d37f60f` | Remove Windows installer job | #1 Bundled Python |
| `1d6da0b` | Switch Mac to ubuntu-latest | #2 wkhtmltopdf |
| `fddbc9c` | Remove GHCR push, reuse images | #3 Permissions, #4 Redundant builds |

---

## How to Build Windows Installer Locally

Since the Windows installer requires the `py-dist/` folder which is too large for git:

```bash
# On a Windows machine with py-dist/ folder present:
# 1. Install Inno Setup: https://jrsoftware.org/isdl.php
# 2. Right-click installer_config.iss → Compile
# 3. Output: dist/Kodys Foot Clinik Installer.exe
```

---

## How to Re-enable GHCR Push (Future)

If you want to push Docker images to `ghcr.io` in the future:

1. Create a **Personal Access Token** at GitHub → Settings → Developer settings → PAT
2. Grant scope: `write:packages`, `read:packages`
3. Add as repo secret: Settings → Secrets → `CR_PAT`
4. Update workflow to use `${{ secrets.CR_PAT }}` instead of `${{ secrets.GITHUB_TOKEN }}`
