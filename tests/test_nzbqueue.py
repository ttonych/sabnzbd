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

import sabnzbd.nzbqueue as nzbqueue

from sabnzbd.nzbqueue import NzbQueue


def _make_job(name, added, priority=0):
    return SimpleNamespace(
        final_name=name,
        bytes=100,
        avg_date=0,
        remaining=0,
        time_added=added,
        priority=priority,
        removed_from_queue=False,
    )


def test_sort_queue_time_added(monkeypatch):
    queue = NzbQueue()

    older = _make_job("older", 100)
    newer = _make_job("newer", 200)
    unknown = _make_job("unknown", None)

    queue._NzbQueue__nzo_list = [newer, unknown, older]

    monkeypatch.setattr(queue, "save", lambda *args, **kwargs: None)

    queue.sort_queue("time_added", "asc")
    assert [job.final_name for job in queue._NzbQueue__nzo_list] == ["unknown", "older", "newer"]

    queue._NzbQueue__nzo_list = [newer, unknown, older]

    queue.sort_queue("time_added", "desc")
    assert [job.final_name for job in queue._NzbQueue__nzo_list] == ["newer", "older", "unknown"]


def test_backfill_time_added(monkeypatch):
    queue = NzbQueue()

    first = _make_job("first", None)
    second = _make_job("second", 0)

    queue._NzbQueue__nzo_list = [first, second]

    monkeypatch.setattr(nzbqueue.time, "time", lambda: 123)

    changed = queue._backfill_time_added()

    assert changed is True
    assert [job.time_added for job in queue._NzbQueue__nzo_list] == [121, 122]


def test_backfill_time_added_respects_existing(monkeypatch):
    queue = NzbQueue()

    missing = _make_job("missing", None)
    existing = _make_job("existing", 50)
    second_missing = _make_job("second_missing", 0)

    queue._NzbQueue__nzo_list = [missing, existing, second_missing]

    monkeypatch.setattr(nzbqueue.time, "time", lambda: 999)

    changed = queue._backfill_time_added()

    assert changed is True
    assert [job.time_added for job in queue._NzbQueue__nzo_list] == [48, 50, 49]


def test_backfill_time_added_noop():
    queue = NzbQueue()

    first = _make_job("first", 100)
    second = _make_job("second", 200)

    queue._NzbQueue__nzo_list = [first, second]

    changed = queue._backfill_time_added()

    assert changed is False


def test_sort_queue_backfill_triggers_save(monkeypatch):
    queue = NzbQueue()

    existing = _make_job("existing", 50)
    missing = _make_job("missing", None)

    queue._NzbQueue__nzo_list = [existing, missing]

    called = []

    def fake_save(*args, **kwargs):
        called.append(True)

    monkeypatch.setattr(queue, "save", fake_save)

    queue.sort_queue("time_added", "asc")

    assert called == [True]
    assert all(job.time_added for job in queue._NzbQueue__nzo_list)
