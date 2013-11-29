#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fixtures for testing"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import time
import random
import job_queue


class JobAlwaysCrashes(job_queue.Job):
    def do(self):
        1 / 0


unicode_job_result = u"abcdé"


class JobWithUnicode(job_queue.Job):
    def do(self):
        return unicode_job_result


class JobWithSleep(job_queue.Job):
    def do(self):
        from thread import get_ident
        print("JobWithSleep with args:", self.arguments, "on thread:", str(get_ident()))
        time.sleep(random.randrange(1, 3) / 10.0)
        print("JobWithSleep", self.arguments, "DONE")


job1_arguments = (42,)
