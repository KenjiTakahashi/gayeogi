; This is a part of Fetcher @ http://github.com/KenjiTakahashi/Fetcher/
; Karol "Kenji Takahashi" Wozniak (C) 2010 - 2011
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
OutFile "Fetcher-0.5-x86.exe"

InstallDir "$PROGRAMFILES\Fetcher"

InstallDirRegKey HKLM "Software\Fetcher" "Install_Dir"

RequestExecutionLevel admin

;Pages

!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Fetcher (required)"
SectionIn RO
    SetOutPath "$INSTDIR"
    
    File "dist\_hashlib.pyd"
    File "dist\_s*"
    File "dist\bz2.pyd"
    File "dist\f*"
    File "dist\m*"
    File "dist\PyQt4.Qt*"
    File "dist\Qt*"
    File "dist\py*dll"
    File "dist\pyexpat.pyd"
    File "dist\s*"
    File "dist\u*"
    File "dist\w*"

    SetOutPath "$INSTDIR\qt4_plugins"

    File /r "dist\qt4_plugins\*"

    SetOutPath "$INSTDIR\plugins"

    File "dist\plugins\__init__.pyc"
    
    WriteRegStr HKLM "Software\Fetcher" "Install_Dir" "$INSTDIR"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Fetcher" "DisplayName" "Fetcher"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Fetcher" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Fetcher" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Fetcher" "NoRepair" 1
    WriteUninstaller "uninstall.exe"
SectionEnd

Section "Player"
    SetOutPath "$INSTDIR"

    File "dist\phonon4.dll"
    File "dist\PyQt4.phonon.pyd"
    File "dist\_bsddb.pyd"

    SetOutPath "$INSTDIR\plugins"

    File "dist\plugins\player.pyc"
SectionEnd

Section "Last.FM/Libre.FM"
    SetOutPath "$INSTDIR\plugins"

    File "dist\plugins\lastfm.pyc"
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
    Delete "$INSTDIR\*"
    Delete "$INSTDIR\plugins\*"
    Delete "$INSTDIR\qt4_plugins\codecs\*"
    Delete "$INSTDIR\qt4_plugins\iconengines\*"
    Delete "$INSTDIR\qt4_plugins\imageformats\*"
    Delete "$INSTDIR\qt4_plugins\phonon_backend\*"
    Delete "$INSTDIR\uninstall.exe"

    ; Remove shortcuts, if any
    Delete "$SMPROGRAMS\Fetcher\*.*"

    ; Remove directories used
    RMDir "$SMPROGRAMS\Fetcher"
    RMDir "$INSTDIR\plugins"
    RMDir "$INSTDIR\qt4_plugins\codecs"
    RMDir "$INSTDIR\qt4_plugins\iconengines"
    RMDir "$INSTDIR\qt4_plugins\imagesformats"
    RMDir "$INSTDIR\qt4_plugins\phonon_backend"
    RMDir "$INSTDIR"

SectionEnd
