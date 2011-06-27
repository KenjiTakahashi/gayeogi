# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2010
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QPushButton

class ConfirmationDialog(QDialog):
    def __init__(self, parent = None):
        QDialog.__init__(self, parent)
        save = QPushButton(self.trUtf8('&Save'))
        save.clicked.connect(self.close)
        close = QPushButton(self.trUtf8('Close &without saving'))
        close.clicked.connect(self.close)
        cancel = QPushButton(self.trUtf8('&Cancel'))
        cancel.clicked.connect(self.close)
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(save, QDialogButtonBox.AcceptRole)
        self.buttons.addButton(close, QDialogButtonBox.HelpRole)
        self.buttons.addButton(cancel, QDialogButtonBox.RejectRole)
        label = QLabel(self.trUtf8(
            "You've got some unsaved changes. What would you like to do?"))
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.buttons)
        self.setLayout(layout)
