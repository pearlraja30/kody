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
SetupIconFile=C:\Users\ant000000\Documents\Kodys\Kodys\appicon.ico
OutputDir=C:\Users\ant000000\Documents\
OutputBaseFilename="Kodys Foot Clinik Installer.exe"
Compression=lzma
SolidCompression=yes
WizardStyle=modern


[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\ant000000\Documents\Kodys\Kodys\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

 


