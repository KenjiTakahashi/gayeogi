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


from PyQt4.QtGui import QSortFilterProxyModel
import re


class Filter(QSortFilterProxyModel):
    def __init__(self, model, parent=None):
        """Creates new Filter instance.

        :model: Source model.
        :parent: Parent object.
        """
        super(Filter, self).__init__(parent)
        self.arguments = dict()
        self.adr = dict()
        self._num_adr = {
            u'a': 123,
            u'd': 234,
            u'r': 345
        }
        self.setSourceModel(model)
        self.setDynamicSortFilter(True)

    def setSelection(self, selected, deselected):
        """Middleware for Model.setSelection."""
        self.sourceModel().setSelection(
            [e.model().mapToSource(e) for e in selected.indexes()],
            [e.model().mapToSource(e) for e in deselected.indexes()]
        )

    def setFilter(self, filter):
        """@todo: Docstring for setFilter

        :filter: @todo
        :returns: @todo
        """
        self.arguments = dict()
        self.adr = dict()
        adr = [u'a', u'd', u'r', u'not a', u'not d', u'not r']
        for a in unicode(filter).split(u'|'):
            temp = a.split(u':')
            if len(temp) == 1 and temp[0] in adr:
                temp2 = temp[0].split(u' ')
                if len(temp2) == 2:
                    self.adr[temp2[1]] = False
                else:
                    self.adr[temp2[0]] = True
                continue
            if len(temp) != 2 or temp[1] == u'':
                break
            self.arguments[temp[0].lower()] = temp[1].lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        """Reimplemented from QSortFilterProxyModel.filterAcceptsRow."""
        if self.arguments:
            for k, v in self.arguments.iteritems():
                for i in xrange(self.columnCount()):
                    sourceModel = self.sourceModel()
                    column = sourceModel.headerData(i).lower()
                    index = sourceModel.index(row, i, parent)
                    data = sourceModel.data(index).lower()
                    if not column == k:
                        break
                    if re.search(v, unicode(data)):
                        return True
            return False
        if self.adr:
            for k, v in self.adr.iteritems():
                for i in xrange(self.columnCount()):
                    sourceModel = self.sourceModel()
                    index = sourceModel.index(row, i, parent)
                    data = sourceModel.data(index, self._num_adr[k])
                    if data == v:
                        return True
            return False
        return True

    def lessThan(self, left, right):
        """Reimplemented from QSortFilterProxyModel.lessThan."""
        source = self.sourceModel()
        lcolumn = source.headerData(left.column())
        rcolumn = source.headerData(right.column())
        leftd = source.data(left)
        rightd = source.data(right)
        if lcolumn == u'#' and rcolumn == u'#':
            track1 = int(leftd.split(u'/')[0])
            track2 = int(rightd.split(u'/')[0])
            album1 = source.data(source.index(left.row(), 1, left.parent()))
            album2 = source.data(source.index(right.row(), 1, right.parent()))
            return album1 < album2 or track1 < track2
        return leftd < rightd
