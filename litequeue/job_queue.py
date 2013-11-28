#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""1 liner to explain this project"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import argparse
import config
import sqlite_utilities
import job_exceptions


class Job(object):
    def __init__(self, arguments):
        self.arguments = arguments

    def do(self):
        return self.arguments


class Manager(object):
    def __init__(self, job_prototype):
        self.job_prototype = job_prototype
        self.tbl_prefix = "default"
        self.job_table = "jobs_" + self.tbl_prefix
        #self.db_conn = config.db_conn
        sqlite_utilities.make_table(self.job_table)

    def count_jobs(self):
        return sqlite_utilities.count_jobs(self.job_table)

    def add_job(self, arguments):
        return sqlite_utilities.add_job(self.job_table, arguments)

    def get_available_job(self):
        return sqlite_utilities.get_available_job(self.job_table)

    def count_job_states(self):
        return sqlite_utilities.count_job_states(self.job_table)

    def get_completed_job(self, job_status=sqlite_utilities.JOB_STATUS_SUCCEEDED):
        return sqlite_utilities.get_result(self.job_table, job_status)

    def do_single_job(self):
        job_id, arguments = self.get_available_job()
        try:
            job = self.job_prototype(arguments)
            result = job.do()
            sqlite_utilities.change_job_status(self.job_table, job_id, sqlite_utilities.JOB_STATUS_SUCCEEDED, result=result)
        except Exception as err:
            sqlite_utilities.change_job_status(self.job_table, job_id, sqlite_utilities.JOB_STATUS_FAILED, result=str(err))


class ProcessJobsInSeries(object):
    def __init__(self, manager):
        self.manager = manager

    def process(self, stop_when_all_jobs_completed=True):
        while True:
            try:
                print("tring to do a job")
                self.manager.do_single_job()
            except job_exceptions.NoJobsException:
                if stop_when_all_jobs_completed:
                    break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Project description')
    #parser.add_argument('positional_arg', help='required positional argument')
    #parser.add_argument('--optional_arg', '-o', help='optional argument', default="Ian")

    args = parser.parse_args()
    print("These are our args:")
    print(args)
    #print("{} {}".format(args.positional_arg, args.optional_arg))

    #config.logging.info("This is an example log message")

    mgr = Manager()
