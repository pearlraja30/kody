# iOS Application Roadmap - KODYS Medical

This document outlines the technical strategy for porting the KODYS Django/Python application to a native iOS app using a **Hybrid Shell** approach.

## 📱 Architecture: The "Hybrid" Bridge

Since running a full Python/Django server on iOS is resource-intensive and restricted by the App Store (W^X policies), we will use **Capacitor** to bridge the existing web UI with native iOS features.

### 1. Data Mode: Local vs. Cloud
- **Initial Phase**: The app will point to a **secured local webview** of the Django server (hosted on the clinic's local network or via a secure tunnel).
- **Final Phase**: We will implement a lightweight **Offline-Sync Engine** using `Capacitor SQLite` to allow data capture even when the clinic's main server is unreachable.

### 2. Native Feature Integration
The following features will be "Native" on the iPhone:
- **Patient Details Capture**: Using `@capacitor/camera` to scan documents and take patient photos.
- **Reports**: Using `@capacitor/filesystem` and `@capacitor/browser` to download and view PDFs natively.
- **Biometric Security**: Using `capacitor-native-biometric` for FaceID/TouchID login.

## 🛠️ Build Process (Future)

1.  **Frontend Export**: Export the Django templates and static assets into the `www/` folder.
2.  **Native Shell**: Initialize the iOS project:
    ```bash
    npx cap add ios
    npx cap open ios
    ```
3.  **Xcode Build**: Finalize the app in Xcode for submission to the App Store.

## 📅 Timeline Strategy

- **Phase A (Native macOS)**: Complete (v2.2.48).
- **Phase B (iOS Foundation)**: Initiated (Capacitor configuration created).
- **Phase C (iOS Beta)**: Integration of Camera and local data sync (Target: v2.3.0).
