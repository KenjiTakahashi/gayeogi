!include "MUI2.nsh"

Name "Fetcher"
OutFile "Fetcher-0.3-x86.exe"

InstallDir "$PROGRAMFILES\Fetcher"

InstallDirRegKey HKLM "Software\Fetcher" "Install_Dir"

RequestExecutionLevel admin

;Pages

!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Fetcher (required)"
	SetOutPath "$INSTDIR"
	
	File "dist\*"
	
	WriteRegStr HKLM "Software\Fetcher" "Install_Dir" "$INSTDIR"
	
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Fetcher" "DisplayName" "Fetcher"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Fetcher" "UninstallString" '"$INSTDIR\uninstall.exe"'
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Fetcher" "NoModify" 1
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Fetcher" "NoRepair" 1
	WriteUninstaller "uninstall.exe"
SectionEnd

Section "Start Menu Shortcuts"
	CreateDirectory "$SMPROGRAMS\Fetcher"
	CreateShortCut "$SMPROGRAMS\Fetcher\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
	CreateShortCut "$SMPROGRAMS\Fetcher\Fetcher.lnk" "$INSTDIR\fetcher.exe" "" "$INSTDIR\fetcher.exe" 0
SectionEnd

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Fetcher"
  DeleteRegKey HKLM "Software\Fetcher"

  ; Remove files and uninstaller
  Delete $INSTDIR\*
  Delete $INSTDIR\uninstall.exe

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\Fetcher\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\Fetcher"
  RMDir "$INSTDIR"

SectionEnd