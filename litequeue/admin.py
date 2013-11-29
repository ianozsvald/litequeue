#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for start_here"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
from litequeue import sqlite_utilities
from litequeue import config


if __name__ == "__main__":
    # list failed jobs
    db_conn = config.get_db_connection()
    service = "jobs_get_twitter_profiles"
    # list all the broken jobs
    #broken_status = sqlite_utilities.JOB_STATUS_FAILED
    broken_status = sqlite_utilities.JOB_STATUS_IN_PROCESS
    print("Showing and resetting for status:", broken_status)
    for job_id, result in sqlite_utilities.get_results(service, broken_status, db_conn):
        print(job_id, result)
        new_status = sqlite_utilities.JOB_STATUS_AVAILABLE
        result = None  # reset to an empty state
        #sqlite_utilities.change_job_status(service, job_id, new_status, db_conn, result)

