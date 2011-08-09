; This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
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
!include "Sections.nsh"

Name "gayeogi"
OutFile "gayeogi-0.6.1-x86.exe"

InstallDir "$PROGRAMFILES\gayeogi"

InstallDirRegKey HKCU "Software\gayeogi" "Install_Dir"

RequestExecutionLevel user

!define MUI_ABORTWARNING

;Language dialog

!define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
!define MUI_LANGDLL_REGISTRY_KEY "Software\gayeogi"
!define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

;Pages

!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Polish"

!insertmacro MUI_RESERVEFILE_LANGDLL

Section "!gayeogi"
SectionIn RO
    SetOutPath "$INSTDIR"
    
    File "dist\_hashlib.pyd"
    File "dist\_s*"
    File "dist\bz2.pyd"
    File "dist\g*"
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
    
    WriteRegStr HKCU "Software\gayeogi" "Install_Dir" "$INSTDIR"
    
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\gayeogi" "DisplayName" "gayeogi"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\gayeogi" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\gayeogi" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\gayeogi" "NoRepair" 1
    WriteUninstaller "uninstall.exe"
SectionEnd

SectionGroup "Plugins"
    Section "Player" PLAY
        SetOutPath "$INSTDIR"

        File "dist\phonon4.dll"
        File "dist\PyQt4.phonon.pyd"
        File "dist\_bsddb.pyd"

        SetOutPath "$INSTDIR\plugins"

        File "dist\plugins\player.pyc"
    SectionEnd
    Section "-PolishPlayer" POLPLAY
        SetOutPath "$INSTDIR\plugins\langs"

        File "dist\plugins\langs\player_pl_PL.qm"
    SectionEnd

    Section "Last.FM/Libre.FM" FM
        SetOutPath "$INSTDIR\plugins"

        File "dist\plugins\lastfm.pyc"
    SectionEnd
    Section "-PolishLast.FM" POLFM
        SetOutPath "$INSTDIR\plugins\langs"

        File "dist\plugins\langs\lastfm_pl_PL.qm"
    SectionEnd
SectionGroupEnd

SectionGroup "Languages"
    Section "English"
    SectionIn RO
    SectionEnd
    Section "Polish" POL
        SetOutPath "$INSTDIR\langs"
        
        File "dist\langs\main_pl_PL.qm"
    SectionEnd
SectionGroupEnd

SectionGroup "Databases"
    Section "metal-archives.com" MA
        SetOutPath "$INSTDIR\bees"

        File "dist\bees\metalArchives.pyc"
    SectionEnd
    Section "musicbrainz.org" MB
        SetOutPath "$INSTDIR\bees"

        File "dist\bees\musicbrainz.pyc"
    SectionEnd
    Section "-lxml" LXML
        SetOutPath "$INSTDIR"
    
        File "dist\lxml*"
    SectionEnd
SectionGroupEnd

Section "Start Menu Shortcuts"
    CreateDirectory "$SMPROGRAMS\gayeogi"
    CreateShortCut "$SMPROGRAMS\gayeogi\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
    CreateShortCut "$SMPROGRAMS\gayeogi\gayeogi.lnk" "$INSTDIR\gayeogi.exe" "" "$INSTDIR\gayeogi.exe" 0
SectionEnd

Function .onInit
    !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Function .onSelChange
    !insertmacro SectionFlagIsSet ${MA} ${SF_SELECTED} Select Second
    Second:
    !insertmacro SectionFlagIsSet ${MB} ${SF_SELECTED} Select Unselect
    Unselect:
    !insertmacro UnselectSection ${LXML}
    Goto Next
    Select:
    !insertmacro SelectSection ${LXML}
    Next:
    !insertmacro SectionFlagIsSet ${PLAY} ${SF_SELECTED} PSelect PSecond
    PSecond:
    !insertmacro UnselectSection ${FM}
    !insertmacro SetSectionFlag ${FM} ${SF_RO}
    Goto Next2
    PSelect:
    !insertmacro ClearSectionFlag ${FM} ${SF_RO}
    Next2:
    !insertmacro SectionFlagIsSet ${POL} ${SF_SELECTED} LSelect End
    LSelect:
    !insertmacro SectionFlagIsSet ${PLAY} ${SF_SELECTED} PlaySelect PlayUnselect
    PlaySelect:
    !insertmacro SelectSection ${POLPLAY}
    Goto FMCheck
    PlayUnselect:
    !insertmacro UnselectSection ${POLPLAY}
    FMCheck:
    !insertmacro SectionFlagIsSet ${FM} ${SF_SELECTED} FMSelect FMUnselect
    FMSelect:
    !insertmacro SelectSection ${POLFM}
    Goto End
    FMUnselect:
    !insertmacro UnselectSection ${POLFM}
    End:
FunctionEnd

Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\gayeogi"
    DeleteRegKey HKCU "Software\gayeogi"

    ; Remove files and directories
    Delete "$INSTDIR\qt4_plugins\phonon_backend\phonon_ds94.dll"
    Delete "$INSTDIR\qt4_plugins\imageformats\qtiff4.dll"
    Delete "$INSTDIR\qt4_plugins\imageformats\qsvg4.dll"
    Delete "$INSTDIR\qt4_plugins\imageformats\qmng4.dll"
    Delete "$INSTDIR\qt4_plugins\imageformats\qjpeg4.dll"
    Delete "$INSTDIR\qt4_plugins\imageformats\qico4.dll"
    Delete "$INSTDIR\qt4_plugins\imageformats\qgif4.dll"
    Delete "$INSTDIR\qt4_plugins\iconengines\qsvgicon4.dll"
    Delete "$INSTDIR\qt4_plugins\codecs\qtwcodecs4.dll"
    Delete "$INSTDIR\qt4_plugins\codecs\qkrcodecs4.dll"
    Delete "$INSTDIR\qt4_plugins\codecs\qjpcodecs4.dll"
    Delete "$INSTDIR\qt4_plugins\codecs\qcncodecs4.dll"
    Delete "$INSTDIR\plugins\langs\player_pl_PL.qm"
    Delete "$INSTDIR\plugins\langs\lastfm_pl_PL.qm"
    Delete "$INSTDIR\plugins\player.pyc"
    Delete "$INSTDIR\plugins\lastfm.pyc"
    Delete "$INSTDIR\plugins\__init__.pyc"
    Delete "$INSTDIR\langs\main_pl_PL.qm"
    Delete "$INSTDIR\bees\musicbrainz.pyc"
    Delete "$INSTDIR\bees\metalArchives.pyc"
    Delete "$INSTDIR\win32api.pyd"
    Delete "$INSTDIR\uninstall.exe"
    Delete "$INSTDIR\unicodedata.pyd"
    Delete "$INSTDIR\sip.pyd"
    Delete "$INSTDIR\select.pyd"
    Delete "$INSTDIR\QtGui4.dll"
    Delete "$INSTDIR\QtCore4.dll"
    Delete "$INSTDIR\pywintypes27.dll"
    Delete "$INSTDIR\python27.dll"
    Delete "$INSTDIR\PyQt4.QtGui.pyd"
    Delete "$INSTDIR\PyQt4.QtCore.pyd"
    Delete "$INSTDIR\PyQt4.phonon.pyd"
    Delete "$INSTDIR\pyexpat.pyd"
    Delete "$INSTDIR\phonon4.dll"
    Delete "$INSTDIR\msvcr90.dll"
    Delete "$INSTDIR\msvcp90.dll"
    Delete "$INSTDIR\msvcm90.dll"
    Delete "$INSTDIR\Microsoft.VC90.CRT.manifest"
    Delete "$INSTDIR\lxml.etree.pyd"
    Delete "$INSTDIR\gayeogi.exe.manifest"
    Delete "$INSTDIR\gayeogi.exe"
    Delete "$INSTDIR\bz2.pyd"
    Delete "$INSTDIR\_ssl.pyd"
    Delete "$INSTDIR\_socket.pyd"
    Delete "$INSTDIR\_hashlib.pyd"
    Delete "$INSTDIR\_bsddb.pyd"
    RMDir "$INSTDIR\qt4_plugins\phonon_backend"
    RMDir "$INSTDIR\qt4_plugins\imageformats"
    RMDir "$INSTDIR\qt4_plugins\iconengines"
    RMDir "$INSTDIR\qt4_plugins\codecs"
    RMDir "$INSTDIR\plugins\langs"
    RMDir "$INSTDIR\qt4_plugins"
    RMDir "$INSTDIR\plugins"
    RMDir "$INSTDIR\langs"
    RMDir "$INSTDIR\bees"
    RMDir "$INSTDIR"
SectionEnd

Function un.onInit
    !insertmacro MUI_UNGETLANGUAGE
FunctionEnd
