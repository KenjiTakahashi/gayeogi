# -*- coding: utf-8 -*-
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

from pkgutil import iter_modules
from os.path import dirname
from sys import platform

__tmp__ = []
if platform == 'win32':
    dir_ = 'plugins'
else:
    dir_ = dirname(__file__)
for _, name, _ in iter_modules([dir_]):
    try:
        __import__(u'gayeogi.plugins.' + name)
    except Exception, e:
        pass
    else:
        __tmp__.append(name)

__all__ = []
while __tmp__:
    tmp = __tmp__.pop(0)
    e = __import__(u'gayeogi.plugins.' + tmp, globals(),
            locals(), [u'Main'], -1)
    error = False
    for d in e.Main.depends:
        try:
            i = __tmp__.index(d)
        except ValueError:
            if d not in __all__:
                error = True
        else:
            __all__.append(__tmp__[i])
            del __tmp__[i]
    if not error:
        __all__.append(tmp)
