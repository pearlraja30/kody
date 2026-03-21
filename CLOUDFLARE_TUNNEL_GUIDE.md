# Cloudflare Tunnel – Setup & Usage Guide

## Overview

Cloudflare Tunnel (cloudflared) creates a secure, encrypted tunnel from a public URL to your local application — **no sign-up, no port forwarding, completely free**.

---

## Installation

```bash
# macOS (Homebrew)
brew install cloudflared

# Verify installation
cloudflared --version
```

---

## Quick Start (No Account Required)

```bash
# Expose Kodys app running on port 5423
cloudflared tunnel --url http://localhost:5423
```

**Output example:**
```
Your quick Tunnel has been created! Visit it at:
https://random-name-here.trycloudflare.com
```

Share this URL with your client. It works as long as `cloudflared` is running.

---

## Usage with Kodys Application

### Step 1: Start Docker

```bash
cd /Users/rajasekaran/Projects/live/kody
docker-compose up --build -d
```

### Step 2: Start Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:5423
```

### Step 3: Share the URL

Copy the `https://xxxxx.trycloudflare.com` URL and send it to your client.

### Step 4: Client Testing

| Detail | Value |
|--------|-------|
| **Public URL** | `https://xxxxx.trycloudflare.com` |
| **Username** | `admin` |
| **Password** | `admin123` |

---

## Comparison: Cloudflare vs ngrok

| Feature | Cloudflare Tunnel | ngrok |
|---------|-------------------|-------|
| **Cost** | Free | Free (limited) |
| **Sign-up** | Not required | Required |
| **HTTPS** | ✅ Automatic | ✅ Automatic |
| **Custom domain** | Free (with account) | Paid |
| **Speed** | Fast (CDN-backed) | Fast |
| **URL persistence** | New URL each run | New URL each run (free) |
| **Dashboard** | No (quick tunnel) | Yes (http://127.0.0.1:4040) |
| **Rate limiting** | None | Free tier limits |

---

## Commands Reference

```bash
# Start tunnel (quick, no account)
cloudflared tunnel --url http://localhost:5423

# Stop tunnel
# Press Ctrl+C in the terminal, or:
killall cloudflared

# Check version
cloudflared --version

# Update
brew upgrade cloudflared
```

---

## Named Tunnels (Optional – With Cloudflare Account)

For persistent URLs that don't change between restarts:

```bash
# 1. Login to Cloudflare
cloudflared tunnel login

# 2. Create a named tunnel
cloudflared tunnel create kodys-test

# 3. Configure DNS (requires a domain on Cloudflare)
cloudflared tunnel route dns kodys-test kodys.yourdomain.com

# 4. Run the named tunnel
cloudflared tunnel run --url http://localhost:5423 kodys-test
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found: cloudflared` | Run `brew install cloudflared` |
| Tunnel starts but URL not accessible | Ensure Docker app is running on port 5423 |
| Connection refused | Check `docker-compose ps` to verify container is up |
| Slow performance | Normal for tunneled connections; Cloudflare CDN helps |
| Need persistent URL | Use named tunnels with a Cloudflare account (free) |
