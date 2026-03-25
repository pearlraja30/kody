# KODYS Application Fixes & UI Refined Documentation (v2.2.5)

This document provides a technical summary of the UI and backend stabilization fixes implemented to address persistent alignment, navigation, and process-management issues in the KODYS application.

## 1. UI Layout & Responsiveness

### Issue: Overlapping Elements and Fixed Dimensions
- **Problem**: Header, content, and footer often overlapped due to absolute positioning. App icons were in rigid `w3-quarter` boxes that didn't adapt to screen resolution.
- **Fix**: 
  - Migrated the base layout (`page_layout.html`) to a **Flexbox** architecture (`display: flex; flex-direction: column;`).
  - Implemented a dynamic grid for the home page (`home.html`) using Flexbox wrap and `justify-content: flex-start`, ensuring icons align predictably from the left on all screen sizes.
- **Benefit**: The UI now "auto-fits" any screen resolution without horizontal scrolling or weirdly centered orphaned icons.

### Issue: Header Overlap & Alignment
- **Problem**: Search suggestion lists or modal sub-menus would sometimes cover the main navigation header. The 103px offset was insufficient for the actual header height (approx. 127px).
- **Fix**: 
  - Overhauled the header to use **`position: fixed`** with a high-priority `z-index: 10000`.
  - Established a definitive global **140px offset** for the main content and sidebars.
  - Refactored the sub-header in `header.html` to a **Flexbox** layout to eliminate text overlapping (hospital name vs address).
  - Removed competing `z-index` overrides in page templates (Patients/Reports) to restore a clear layering hierarchy.
- **Benefit**: The navigation menu is now truly persistent ("stays always") and perfectly aligned without any overlaps, even on high-resolution screens.

## 2. Visibilty & Interaction

### Issue: Login Screen Contrast
- **Problem**: White text ("Welcome", "Username") was difficult to read against some background color gradients.
- **Fix**:
  - Added a semi-transparent dark background (`rgba(0,0,0,0.3)`) behind the login form.
  - Implemented `.login-welcome-text` with a dedicated shadow for maximum legibility.
  - Set a 90% opaque background for input fields.
- **Benefit**: Clear, accessible login experience regardless of the background image/color.

### Issue: Navigation Feedback
- **Problem**: Users were unsure if a link was clicked or if the page was loading.
- **Fix**:
  - Added **hover effects** to all navigation items and app cards (subtle scaling and background changes).
  - Implemented a **Loading Overlay** and spinner that activates during page transitions and form submissions.
  - Added a `.nav-active` state to highlight the current active menu item.
- **Benefit**: Professional, responsive "feel" with clear visual confirmation of user actions.

## 3. Application Lifecycle & Process Management

### Issue: Process Persistence on Mac OS
- **Problem**: When closing the app on Mac, the Django background process remained active because the app used the Windows-only `taskkill` command.
- **Fix**:
  - Implemented platform-aware termination in `run.py`.
  - Uses `proc.terminate()` and `proc.wait()` on Mac/non-Windows systems to gracefully stop the backend server.
- **Benefit**: Closing the app now cleanly terminates all background processes, preventing port conflicts and memory leaks.

### Issue: Duplicate Quit Confirmation
- **Problem**: Closing the window would sometimes trigger the "Are you sure to quit?" dialog twice.
- **Fix**:
  - Introduced an `is_closing` flag in `MainWindow`.
  - The dialog now only prompts once; subsequent close events (triggered by CEF shutdown) are automatically accepted.
- **Benefit**: A smoother, less "annoying" exit experience.

### Issue: Logout Failure for Certain Users
- **Problem**: Admin or Superuser accounts without a corresponding `TX_ACCOUNTUSER` record were unable to log out properly due to an unhandled exception in the `user_signout` API.
- **Fix**: 
  - Refactored `api.user_signout` to gracefully handle missing account records.
  - Ensured the Django `logout(request)` is always called before redirecting to the sign-in screen.
- **Benefit**: Consistent logout functionality for all users types (Doctors, Admin, Technicians).

### Issue: Header/Body "Collapsed" Overlap
- **Problem**: The content body would sometimes appear too close to or under the sticky header on certain resolutions.
- **Fix**:
  - Added a protective `padding-top: 15px` to the main content container in `page_layout.html`.
- **Benefit**: Predictable vertical spacing between the navigation region and the page content.
### Issue: Silent/Stale Application Startup
- **Problem**: The application could take 10-20 seconds to initialize libraries and start the backend, during which the user saw no visual feedback.
- **Fix**: 
  - Enhanced the `QSplashScreen` in `run.py` with real-time status updates using `splash.showMessage()`).
  - Added `splash.raise_()` and increased `processEvents()` frequency to ensure the splash screen is visible immediately on launch.
  - Added feedback for: *Loading Configuration*, *Compiling Assets*, *Starting Backend Services*, and *Initializing Browser Engine*.
- **Benefit**: Immediate visual confirmation of application activity, ensuring the user is never left wondering if the app is starting.
 
## 4. Windows Installer Optimization

### Issue: Installer "Seeking Permission" & Security Warnings
- **Problem**: The previous installer required Administrative privileges (UAC prompt) to install to Program Files. Additionally, Windows SmartScreen would show a "Windows protected your PC" blue box because the app was not digitally signed.
- **Fix**: 
  - Switched to a **Per-User Installation** model (`PrivilegesRequired=lowest`). The app now installs to the user's Local AppData folder by default, which **removes the need for Admin/UAC permission**.
  - Implemented **Direct-Install (Zero-Wizard)**: Setup now skips almost all wizard pages (Welcome, Folder Select, etc.). It installs in one click to maximize speed and professional feel.
  - **Auto-Desktop Icon**: The installer now creates the desktop shortcut automatically.
  - Added professional **VersionInfo Metadata** (Company, Copyright, Product Name) to the installer. This populate the "Details" tab of the `.exe`, increasing legitimacy.
  - Removed non-standard directory permission overrides that could trigger antivirus false positives.
- **Note on SmartScreen (Blue Box)**: 
  - As the software is not yet "Digitally Signed" with a paid Certificate Authority (e.g., Sectigo or DigiCert), the Windows SmartScreen blue box will still appear for new users.
  - **Action for Clients**: Click **"More Info"** -> **"Run anyway"**. Once the app builds "reputation" (used by multiple clients), the warning will naturally disappear.

## 5. Home Page Layout & Icon Fixes

### Issue: Footer Message Overlap
- **Problem**: As more test icons were added to the home screen, the "Software Version" footer would overlap with the bottom row of icons. This was caused by stray HTML tags and a non-dynamic container structure.
- **Fix**: Refactored `home.html` to remove redundant `</div>` tags and moved the footer into a responsive flex container. The footer now naturally sits below the last icon, regardless of how many icons are added.

### Issue: Broken "Kodys CAN" Icon
- **Problem**: The "Kodys CAN" icon appeared as a broken image because its database entry contained an absolute path that conflicted with the application's media configuration.
- **Fix**: Corrected the SQLite database entry for the "Kodys CAN" record to use the proper relative path (`img/png/Kodys_Can.png`).

**Version History**: 
- v2.2.0: Initial Platinum Release
- v2.2.5: Final Gold Stabilization (v4) - Includes Home Page overlap fix and Icon path correction.
