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
    def __init__(self):
        super(HandlerMock, self).__init__()
        self.messages = list()

    def emit(self, record):
        self.messages.append(record)


class BaseTest(object):
    def setUp(self, handler):
        self.logfilter = LogFilter()
        self.logfilter.levels = set(LogFilter.allLevels.values())
        self.logfilter.scopes = set(LogFilter.allScopes)
        self.logger = logging.getLogger('gayeogitest')
        self.logger.setLevel(logging.DEBUG)
        self.handler = handler()
        self.handler.addFilter(self.logfilter)
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()


class TestLogFilter(BaseTest):
    def setUp(self):
        super(TestLogFilter, self).setUp(HandlerMock)

    def test_added_log_level(self):
        self.logger.added({u'track': 0})
        assert self.handler.messages[0].levelno == 60
        assert self.handler.messages[0].levelname == u'ADDED'
        assert self.handler.messages[0].msg == {u'track': 0}

    def test_removed_log_level(self):
        self.logger.removed({u'track': 0})
        assert self.handler.messages[0].levelno == 70
        assert self.handler.messages[0].levelname == u'REMOVED'
        assert self.handler.messages[0].msg == {u'track': 0}

    def test_should_filter_disabled_level(self):
        self.logfilter.removeLevel(u'Added')
        self.logger.added({u'track': 0})
        assert len(self.handler.messages) == 0

    def test_should_not_filter_enabled_level(self):
        self.logger.added({u'track': 0})
        assert len(self.handler.messages) == 1

    def test_should_filter_disabled_track_scope(self):
        self.logfilter.removeScope(u'Track')
        self.logger.added({u'track': 0})
        assert len(self.handler.messages) == 0

    def test_should_not_filter_other_scopes_with_track_scope_disabled(self):
        self.logfilter.removeScope(u'Track')
        self.logger.added({u'album': 0})
        self.logger.added({u'artist': 0})
        assert len(self.handler.messages) == 2

    def test_should_filter_disabled_all_scopes(self):
        self.logfilter.scopes = set()
        self.logger.added({u'track': 0})
        self.logger.added({u'album': 0})
        self.logger.added({u'artist': 0})
        assert len(self.handler.messages) == 0


class TestHandler(BaseTest):
    def setUp(self):
        super(TestHandler, self).setUp(Handler)
