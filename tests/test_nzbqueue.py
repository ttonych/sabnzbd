#!/usr/bin/python3 -OO
# Copyright 2007-2025 by The SABnzbd-Team (sabnzbd.org)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
tests.test_nzbqueue - Tests for sabnzbd.nzbqueue
"""

from types import SimpleNamespace

from sabnzbd.nzbqueue import NzbQueue


def _make_job(name, added, priority=0):
    return SimpleNamespace(
        final_name=name,
        bytes=100,
        avg_date=0,
        remaining=0,
        time_added=added,
        priority=priority,
    )


def test_sort_queue_time_added():
    queue = NzbQueue()

    older = _make_job("older", 100)
    newer = _make_job("newer", 200)
    unknown = _make_job("unknown", None)

    queue._NzbQueue__nzo_list = [newer, unknown, older]

    queue.sort_queue("time_added", "asc")
    assert [job.final_name for job in queue._NzbQueue__nzo_list] == ["unknown", "older", "newer"]

    queue._NzbQueue__nzo_list = [newer, unknown, older]

    queue.sort_queue("time_added", "desc")
    assert [job.final_name for job in queue._NzbQueue__nzo_list] == ["newer", "older", "unknown"]
