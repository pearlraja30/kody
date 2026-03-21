# Kodys Project - Installer & Sharing Guide

This guide explains how to prepare the application for client testing.

## Option 1: Share as a Modular Folder (Recommended for Fast Testing)

You can bundle all the necessary files into a single ZIP archive that the client can simply extract and run.

1.  **Run the packaging script**:
    ```bash
    python package_for_client.py
    ```
2.  This will create a file named **`Kodys_Foot_Clinik_Package.zip`**.
3.  **Share this ZIP** with the client.
4.  The client just needs to extract it and run `launchapp.bat` or `Kodys Foot Clinik.exe`.

## Option 2: Build a Windows Installer (.exe)

If the client requires a professional installer, use the provided Inno Setup script.

1.  **Transfer the project** to a Windows machine (or VM).
2.  Install [Inno Setup](https://jrsoftware.org/isdl.php).
3.  Right-click on **`installer_config.iss`** in the root directory and select **"Compile"**.
4.  The resulting installer will be in the `dist/` folder.

## Preparation Checklist before Sharing

- [ ] Ensure `app/appsource/db.sqlite3` contains the necessary test data (or is clean).
- [ ] Verify that `config/config.json` has the correct settings for the client environment.
- [ ] If you've made changes to the Django code, ensure they are reflected in the `app/` directory.
