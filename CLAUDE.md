# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Job Notifier** is a full-stack application that monitors job listings from Romanian websites and notifies users. It consists of:

- **Frontend**: React Native (Expo) cross-platform app - runs on iOS, Android, and web
- **Backend API**: Flask server (server.py) - deployed on Render at https://jobnotifier-api-l7ay.onrender.com
- **Scraper**: job_notifier.py - monitors sites and sends email alerts for new jobs
- **GitHub**: Source code at https://github.com/SneeKyTCH/jobnotifier-backend

## Architecture

### Backend (server.py)
- **Framework**: Flask with CORS enabled
- **Job Storage**: Persistent cache in `jobs_cache.json` - stores ALL jobs found
- **Scraping**: Multi-threaded scraper runs at startup and every 30 minutes
- **Data Sources**: eJobs (2 URLs) and OLX
- **Deployment**: Gunicorn on Render (auto-redeploy on git push)

Key endpoints:
- `POST /login`, `POST /register` - Returns `{token, user, message}`
- `GET /jobs` - Returns all cached jobs (58+ from latest run)
- `GET /me`, `GET /profile`, `GET /preferences` - User endpoints
- `POST /saved-jobs`, `GET /saved-jobs`, `DELETE /saved-jobs` - Favorites
- `GET /applications`, `POST /applications` - Application tracking
- `POST /logout` - Logout

### Frontend (app/)
- **Expo v54** with React Native + React Navigation
- **Screens**: AuthScreen (login/register), JobsScreen (list), JobDetailScreen, SavedScreen, SettingsScreen
- **Storage**: AsyncStorage for tokens and user preferences
- **Theme**: Dynamic dark/light mode with ThemeContext
- **API Integration**: app/src/api.js handles all HTTP requests

### Email Notifier (job_notifier.py)
- Runs on schedule (GitHub Actions or local Task Scheduler)
- Emails only **NEW** jobs (tracks seen IDs in job_cache.json)
- Uses Gmail SMTP - configure EMAIL_TAU, EMAIL_SMTP, PAROLA_EMAIL as env vars

## Common Commands

### Frontend (app/)
```bash
cd app
npm install                    # Install dependencies
npm start                      # Start Expo (press 'w' for web, 'a' for Android, 'i' for iOS)
npm run web                    # Start web version directly (http://localhost:8081)
```

### Backend (local testing)
```bash
python server.py               # Run Flask server (http://localhost:5000)
python job_notifier.py         # Run scraper once
```

### Deployment
```bash
git push backend master:main   # Pushes to jobnotifier-backend → auto-redeploy on Render
```

## Critical Implementation Details

### Login Flow
1. App calls `POST /login` with email/password
2. Backend returns `{token, user: {id, username, email}, message}`
3. App saves token to AsyncStorage via `saveToken()`
4. App calls `GET /me` to verify user
5. **Important**: Response MUST include `user` object (not just `user_id`) - app expects this

### Job Caching Strategy
- `server.py`: Stores ALL jobs ever found in `jobs_cache.json` (persistent across restarts)
- `job_notifier.py`: Tracks seen IDs separately, emails only new ones
- Max 10,000 jobs kept in cache (rolling window)
- Background thread in server updates every 30 minutes

### Scraping Notes
- eJobs selectors: `article.job-item`, `div[class*="job-item"]`, `li[class*="job"]`
- OLX selectors: `[data-cy="l-card"]`, `div.offer-wrapper`, `li.offer-item`
- Both use `get_soup()` helper with 5s connect, 8s read timeout
- Failed scrapes are silently skipped; job_notifier.py prints errors to logs

### Web App Notes
- React Native Web has deprecation warnings for `shadow*` and `pointerEvents` props - non-critical
- "Unexpected text node" errors in View - cosmetic UI issues, doesn't block functionality
- CORS is enabled on all endpoints (`CORS(app)`)
- Preflight requests (OPTIONS) must pass access control

## Deployment Checklist

**Before pushing to Render:**
1. Test locally: `npm run web` (app) + `python server.py` (backend)
2. Verify API endpoints return correct JSON structure
3. Check CORS headers on OPTIONS requests
4. Ensure login flow completes (token saved → onAuth called)

**After git push backend master:main:**
1. Render auto-detects changes and redeploys
2. Monitor https://dashboard.render.com/jobnotifier-api-l7ay for status
3. Check logs for scraping errors or startup issues

## Environment Variables (Render)
- PORT: Auto-set by Render (e.g., 10000)
- No other required vars for API (dummy auth, no database)

## Config Files
- **app/src/config.js**: API_URL points to Render endpoint
- **requirements.txt**: Python dependencies (Flask, gunicorn, requests, beautifulsoup4)
- **Procfile**: `web: gunicorn -w 4 -b 0.0.0.0:$PORT server:app`
- **.gitignore**: Excludes `__pycache__`, `*.pyc`, `jobs_cache.json`, `node_modules`

## Debugging
- **App won't connect to API**: Check CORS headers with `curl -X OPTIONS`
- **Login fails**: Verify `/login` returns `user` object, not just `user_id`
- **Jobs not appearing**: Check `server.py` background thread is running; look for scraping timeout errors
- **Render redeploy fails**: Check build logs for syntax errors or missing dependencies in requirements.txt
