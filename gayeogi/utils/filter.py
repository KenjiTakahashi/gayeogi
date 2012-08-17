# -*- coding: utf-8 -*-

from PyQt4.QtGui import QSortFilterProxyModel
from PyQt4.QtCore import Qt
import re


class Filter(QSortFilterProxyModel):
    def __init__(self, model, parent=None):
        """@todo: Docstring for __init__

        :model: @todo
        :parent: @todo
        :returns: @todo

        """
        super(Filter, self).__init__(parent)
        self.arguments = dict()
        self.setSourceModel(model)
        self.setDynamicSortFilter(True)

    def setSelection(self, selected, deselected):
        self.sourceModel().setSelection(selected, deselected)

    def setFilter(self, filter):
        """@todo: Docstring for setFilter

        :filter: @todo
        :returns: @todo

        """
        self.arguments = dict()
        adr = [u'a', u'd', u'r', u'not a', u'not d', u'not r']
        self.adr = dict()
        __num_adr = {
            u'a': 123,
            u'd': 234,
            u'r': 345
        }
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
        """@todo: Docstring for filterAcceptsRow

        :row: @todo
        :parent: @todo
        :returns: @todo

        """
        if self.arguments:
            for k, v in self.arguments.iteritems():
                for i in xrange(self.columnCount()):
                    column = self.sourceModel().headerData(i).lower()
                    index = self.sourceModel().index(row, i, parent).lower()
                    row = self.sourceModel().data(index)
                    if not column == k:
                        break
                    if re.search(v, unicode(row)):
                        return True
            return False
        return True
