# -*- coding: utf-8 -*-
# This is a part of gayeogi @ http://github.com/KenjiTakahashi/gayeogi/
# Karol "Kenji Takahashi" Wozniak (C) 2011
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

import urllib2
from gayeogi.db.bees.beeexceptions import ConnError

def reqread(url):
    """Retrieves data from the given url.

    Also sets up proper User-Agent, so people won't complain.

    Args:
        url (str): url to retrieve from

    """
    req = urllib2.Request(url)
    from gayeogi.main import version
    req.add_header(u'User-Agent', u'gayeogi/' + version +
        u'+http://github.com/KenjiTakahashi/gayeogi')
    try:
        return urllib2.urlopen(req).read()
    except (urllib2.HTTPError, urllib2.URLError):
        raise ConnError()
