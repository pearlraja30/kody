#define MyAppName "Kodys Foot Clinik V2"
#define MyAppVersion "2.0.0 (Official Stable)"
#define MyAppPublisher "Kodys Foot Clinik"
#define MyAppExeName "Kodys Foot Clinik.exe"

[Setup]
AppId={{2F7C5CFB-FAD2-427B-85A5-4AEB28544B55}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
PrivilegesRequired=lowest
DefaultDirName={userappdata}\{#MyAppName}
DisableWelcomePage=yes
DisableDirPage=yes
DisableProgramGroupPage=yes
DefaultGroupName={#MyAppName}
; Replaced absolute path with relative path
SetupIconFile=appicon.ico
OutputDir=dist
OutputBaseFilename="Kodys_Foot_Clinik_v2.2.5"
Compression=lzma
SolidCompression=yes
WizardStyle=modern
VersionInfoVersion=2.2.5.0
VersionInfoCompany=Kodys Foot Clinik
VersionInfoDescription=KODYS Medical Diagnostic Suite
VersionInfoCopyright=Copyright (C) 2026 Kodys Foot Clinik
VersionInfoProductName=Kodys Foot Clinik

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked

[Files]
; Replaced absolute path with relative path to include everything in the root
Source: "app\*"; DestDir: "{app}\app"; Flags: recursesubdirs
Source: "py-dist\*"; DestDir: "{app}\py-dist"; Flags: recursesubdirs
Source: "config\*"; DestDir: "{app}\config"; Flags: recursesubdirs
Source: "Kodys Foot Clinik.exe"; DestDir: "{app}"
Source: "launchapp.bat"; DestDir: "{app}"
Source: "appicon.ico"; DestDir: "{app}"
Source: "readme.txt"; DestDir: "{app}"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon


