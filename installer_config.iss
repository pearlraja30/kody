#define MyAppName "Kodys Foot Clinik V2"
#define MyAppVersion "V2"
#define MyAppPublisher "Kodys Foot Clinik"
#define MyAppExeName "Kodys Foot Clinik.exe"

[Setup]
AppId={{2F7C5CFB-FAD2-427B-85A5-4AEB28544B55}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
; Replaced absolute path with relative path
SetupIconFile=appicon.ico
OutputDir=dist
OutputBaseFilename="Kodys Foot Clinik Installer"
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

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

[Dirs]
Name: "{app}"; Permissions: users-full
