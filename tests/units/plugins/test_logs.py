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


from gayeogi.plugins.logs import LogFilter, Handler
import logging


class HandlerMock(logging.Handler):
    def setTest(self, test):
        self.test = test

    def emit(self, record):
        self.test(record)


class BaseTest(object):
    def setUp(self, handler):
        self.logfilter = LogFilter()
        self.logger = logging.getLogger('gayeogitest')
        self.logger.setLevel(logging.DEBUG)
        self.handler = handler()
        self.handler.addFilter(self.logfilter)
        self.logger.addHandler(self.handler)


class TestLogFilter(BaseTest):
    def setUp(self):
        super(TestLogFilter, self).setUp(HandlerMock)


class TestHandler(BaseTest):
    def setUp(self):
        super(TestHandler, self).setUp(Handler)
