# Kodys Application – Testing Guide

## Quick Start

### 1. Start the Application (Docker)

```bash
cd /Users/rajasekaran/Projects/live/kody
docker-compose up --build -d
```

**Verify it's running:**
```bash
docker-compose logs --tail=50 -f
```

You should see:
```
Starting development server at http://0.0.0.0:5423/
```

### 2. Access Locally

- **URL:** http://localhost:5423/
- **Credentials:** `admin` / `admin123`

### 3. Expose to External Testers (ngrok)

```bash
# Install (one-time)
brew install ngrok

# Start tunnel
ngrok http 5423
```

**Current Public URL:** https://kristy-nonflagrant-puckishly.ngrok-free.dev

> **Note:** The ngrok URL changes each time you restart ngrok (free tier). Share the new URL with the client after each restart.

> **If you get `ERR_NGROK_334`:** An existing tunnel is already running. Either stop it first (`killall ngrok`) or reuse the existing URL shown in the error.

---

## Test Scenarios

### 1. Login & Dashboard
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open the URL | Login page appears |
| 2 | Enter `admin` / `admin123` | Redirects to dashboard |
| 3 | Click "Patients" | Patient list loads (John Doe – ID 100100) |

### 2. ECG Report (Kodys CAN)
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Go to Patients → John Doe | Patient detail page |
| 2 | Click on a CAN test report | Report opens |
| 3 | Verify gridlines | Pink/red ECG grid is clearly visible |
| 4 | Verify centering | Report is centered on the page |
| 5 | Verify load time | Report loads in < 3 seconds |
| 6 | Print the report | Gridlines appear in print preview |

### 3. Reports Page
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Reports" tab | Reports list loads |
| 2 | Search for patient | Search results appear |
| 3 | Filter by date range | Filtered results display |

### 4. Settings / Hospital Profile
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Settings" | Hospital profile page loads |
| 2 | Verify hospital name | "Test Hospital" is displayed |

---

## Docker Commands Reference

```bash
# Start application
docker-compose up --build -d

# View logs
docker-compose logs --tail=100 -f

# Stop application
docker-compose down

# Restart application
docker-compose restart

# Run migrations
docker-compose exec -T web python manage.py migrate

# Create superuser
docker-compose exec -T web python create_admin.py

# Populate sample data
docker-compose exec -T web python populate_data.py
```

## ngrok Commands Reference

```bash
# Start tunnel
ngrok http 5423

# Stop existing tunnel
killall ngrok

# Check tunnel status
# Visit http://127.0.0.1:4040 in browser (ngrok dashboard)
```

## Alternative Tunneling Options

| Tool | Command | Notes |
|------|---------|-------|
| **Cloudflare** | `cloudflared tunnel --url http://localhost:5423` | No sign-up needed |
| **LocalTunnel** | `npx localtunnel --port 5423` | npm-based, simplest |

---

## Environment Details

| Item | Value |
|------|-------|
| Python | 2.7.18 |
| Django | 1.11.29 |
| Database | SQLite3 |
| Docker Platform | linux/amd64 (Rosetta emulation) |
| App Port | 5423 |
| Working Dir (Docker) | `/app/app/appsource/app_config` |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| License key modal appears | Ensure hospital profile is configured in Settings |
| No patients visible | Run `docker-compose exec -T web python populate_data.py` |
| Migration error (table exists) | Run `docker-compose exec -T web python manage.py migrate kodys 0002 --fake` |
| Port 5423 already in use | Stop existing containers: `docker-compose down` |
| ngrok tunnel already exists | `killall ngrok` then restart |
