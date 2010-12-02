; This is a part of Fetcher @ http://github.com/KenjiTakahashi/Fetcher/
; Karol "Kenji Takahashi" Wozniak (C) 2010
;
; This program is free software: you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation, either version 3 of the License, or
; (at your option) any later version.
;
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public License
; along with this program.  If not, see <http://www.gnu.org/licenses/>.
!include "MUI2.nsh"

Name "Fetcher"
OutFile "Fetcher-0.4-x86.exe"

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
