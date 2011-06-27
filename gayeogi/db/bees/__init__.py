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

from pkgutil import iter_modules
from os.path import realpath, dirname

__names__ = list()
__all__ = list()
for _, name, _ in iter_modules([dirname(realpath(__file__))]):
    try:
        tmp = __import__(u'gayeogi.db.bees.' + name, globals(),
                locals(), [u'name'], -1)
    except ImportError:
        pass
    else:
        try:
            tmp.name
        except AttributeError:
            pass
        else:
            __names__.append(tmp.name)
            __all__.append(name)
