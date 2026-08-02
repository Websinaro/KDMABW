# WeBAlert — Kerala Disaster Management App

A full rebuild of the WeBAlert Flutter app: a fast, cool, **dark/AMOLED**
UI for live weather + disaster alerts across Kerala's 14 districts, with
signup-first auth, a distinct **President / State Command Center**
experience, offline caching, and on-device + external backup.

## What's in this zip

```
webalert/          -> the Flutter app (open this folder in Android Studio)
backend/            -> your original FastAPI backend + a small patch (see below)
README.md           -> this file
```

## 1. Backend changes (required)

Your backend at `https://kdmabw.onrender.com` only ever creates `role="user"`
accounts and had no endpoint for the app to fetch "who am I" after login.
Two small, additive changes were made in `backend/`:

1. **`GET /me`** — returns the logged-in user's profile (name, email,
   district, role) given their token. The app needs this right after
   login to know whether to show the citizen dashboard or the President
   command center.
2. **President sign-up via access code** — `POST /register` now accepts
   an optional `access_code` field. If it matches the `PRESIDENT_ACCESS_CODE`
   environment variable (defaults to `KDMA-PRESIDENT-2026` if unset), the
   new account is created with `role="president"` instead of `"user"`.
   Everyone else is unaffected — existing accounts and normal signups keep
   working exactly as before.

**To deploy:** push the updated `backend/` folder to your Render service
(same as before), and optionally set a private `PRESIDENT_ACCESS_CODE`
environment variable in the Render dashboard so the default code isn't
guessable. Only share that code with the actual President / State
Coordinator.

## 2. Running the Flutter app

1. Open the `webalert/` folder in Android Studio (File → Open).
2. Let it prompt you to run `flutter pub get` (or run it yourself in the
   terminal from inside `webalert/`).
3. Plug in a device or start an emulator, then Run.
4. The backend URL is already set to `https://kdmabw.onrender.com` in
   `lib/services/api_service.dart` — change `ApiService.baseUrl` if you
   ever move backends.

> Render's free tier spins down when idle, so the very first request after
> a while can take 20–50s to "wake up" — the app shows a friendly loading
> message and uses a 50s timeout instead of failing fast.

## 3. What the app does

### Signup → Login (in that order)
- New users always sign up first (name, email, phone, district, password).
- A **"President / State Coordinator"** toggle on the signup form reveals
  an access-code field — only accounts created with the correct code get
  the president role from the backend.
- Login is a single form for everyone. After login, the app calls `/me`
  to find out the account's role and routes accordingly. President
  accounts see a short "President Access Granted" screen before landing
  on the Command Center.

### Citizen experience
- **Weather tab**: GPS-based, Google-Weather-style dashboard — big
  gradient header with current temp/condition, an hourly strip with a
  smooth temperature trend line, a 7-day outlook, and a details grid
  (humidity, wind, UV, pressure, sunrise/sunset, air quality).
- **Districts tab**: browse live conditions for all 14 districts, your
  own district is marked.
- Pull to refresh anywhere; a cached copy is shown automatically when
  offline, with a clear "offline" indicator.

### President experience
- **Command Center tab** (replaces "Weather"): a live grid of all 14
  districts with alert-level colour coding and a summary strip (how many
  districts are Clear / Watch / Warning / Severe). Tapping any district
  opens its full Google-Weather-style detail view.

### Dark, battery-friendly UI
- True black (`#000000`) backgrounds throughout — on OLED/AMOLED screens
  (the vast majority of modern Android phones) black pixels draw
  effectively no power, so this is a genuine battery saving, not just a
  visual choice.
- No heavy animation libraries, no downloaded fonts, minimal ripple
  effects, `const` widgets wherever possible, and a lightweight
  hand-rolled chart (`CustomPainter`) instead of a full charting package —
  keeps the app fast and responsive on lower-end devices too.

### Permissions
- **Location** (fine + coarse): requested with a clear explanation on
  first launch, used only to fetch weather for your position.
- **Internet**: declared in the manifest (no runtime prompt needed on
  Android), required to reach the backend.
- **Storage**: only requested when you tap "Backup Now" in Profile.

### Backup & data storage
- The app **always** keeps your profile and latest weather cached on
  the device (SharedPreferences) so it still shows something useful
  offline — no action needed.
- From **Profile → Backup & Restore** you can additionally save a
  portable JSON copy to `Documents/WeBAlert/webalert_backup.json` — a
  folder outside the app's private sandbox, visible in any file manager
  and preserved even if the app is uninstalled. If broad storage access
  isn't granted, it automatically falls back to the app's own external
  folder so backup/restore still works.

## 4. Notes & next steps

- **App icon**: the project ships with the default Flutter launcher icon.
  Add your own via `flutter_launcher_icons` or by replacing the files in
  `android/app/src/main/res/mipmap-*`.
- **Signing**: release builds currently sign with the debug key so
  `flutter build apk` works out of the box. Add your own keystore in
  `android/app/build.gradle.kts` before publishing.
- **minSdkVersion** is set to 23 (Android 6.0+) for broad device
  compatibility while keeping modern permission APIs simple.
