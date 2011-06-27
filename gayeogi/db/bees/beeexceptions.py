# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2010 - 2011
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

class Error(Exception):
    """General Error class."""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class NoBandError(Error):
    """Raised in case specified band has not been found in the database."""
    def __init__(self):
        self.message = u'No such band has been found.'

class ConnError(Error):
    """Raised in case an connection error appeared."""
    def __init__(self):
        self.message = u'An unknown error occurred (no internet?).'
