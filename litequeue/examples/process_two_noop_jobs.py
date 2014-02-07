#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Trivial demo doing almost no work on some user-supplied args to a user-supplied function"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
from functools import partial
from litequeue import job_queue


def simple_work_fn(arguments):
    return "This is the answer using args: " + repr(arguments)

# make a manager that take the user's work fn and a table name
manager = job_queue.Manager(partial(job_queue.SimpleJob, simple_work_fn), tbl_prefix="counting")
processor = job_queue.ProcessJobsInSeries(manager)

# add two jobs
for follower_id in ["arguments_1", "arguments_2"]:
    manager.add_job({'my_identifier': str(follower_id)})

print("Before processing:")
print(manager.count_job_states())
print("Now to process...")
processor.process()
print("After processing:")
print(manager.count_job_states())

print("\nResults:")
for result in manager.completed_jobs():
    print(result)
