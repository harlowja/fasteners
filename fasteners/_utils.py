# -*- coding: utf-8 -*-

# Copyright (C) 2015 Yahoo! Inc. All Rights Reserved.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


try:
    from time import monotonic as now
except ImportError:
    from time import time as now


class StopWatch(object):
    """A really basic stop watch."""

    def __init__(self, duration=None):
        self.duration = duration
        self.started_at = None
        self.stopped_at = None

    def elapsed(self):
        if self.stopped_at is not None:
            t = self.stopped_at
        else:
            t = now()
        return t - self.started_at

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stopped_at = now()

    def start(self):
        self.started_at = now()
        self.stopped_at = None

    def expired(self):
        if self.duration is None:
            return False
        else:
            e = self.elapsed()
            if e > self.duration:
                return True
            return False
