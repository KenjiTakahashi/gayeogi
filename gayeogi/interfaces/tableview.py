# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi
# Karol "Kenji Takahashi" Woźniak © 2012
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


from PyQt4.QtGui import QTableView, QMenu, QCursor
from PyQt4.QtCore import Qt


class TableView(QTableView):
    """Docstring for TableView """

    def __init__(self, state, parent=None):
        """@todo: to be defined

        :parent: @todo
        """
        super(TableView, self).__init__(parent)
        self.setSelectionMode(self.ExtendedSelection)
        self.setSelectionBehavior(self.SelectRows)
        self.setEditTriggers(self.NoEditTriggers)
        self.setShowGrid(False)
        self.setCornerButtonEnabled(False)
        self.setWordWrap(False)
        vheader = self.verticalHeader()
        vheader.setHidden(True)
        hheader = self.horizontalHeader()
        hheader.setStretchLastSection(True)
        hheader.setDefaultAlignment(Qt.AlignLeft)
        hheader.setHighlightSections(False)
        hheader.setMovable(True)
        hheader.setContextMenuPolicy(Qt.CustomContextMenu)
        hheader.customContextMenuRequested.connect(self.showHeaderContextMenu)
        # This restores state over and over for every column added.
        # FIXME: Restore state once (somehow).
        #hheader.sectionCountChanged.connect(
            #lambda: self.horizontalHeader().restoreState(state)
        #)

    def showHeaderContextMenu(self):
        """@todo: Docstring for showHeaderContextMenu """
        menu = QMenu()
        model = self.model()
        for i in xrange(model.columnCount()):
            action = menu.addAction(
                model.headerData(i, Qt.Horizontal, Qt.DisplayRole).toString()
            )
            action.setProperty(u'column', i)
            action.setCheckable(True)
            if not self.isColumnHidden(i):
                action.setChecked(True)
        menu.triggered.connect(self.showHideColumn)
        menu.exec_(QCursor.pos())

    def showHideColumn(self, action):
        """@todo: Docstring for showHideColumn

        :action: @todo
        """
        column = action.property(u'column').toInt()[0]
        self.setColumnHidden(column, not self.isColumnHidden(column))
