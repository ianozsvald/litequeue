#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Lightweight queue using SQLite3"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import argparse
from functools import partial
from litequeue import config
from litequeue import sqlite_utilities
from litequeue import job_exceptions


class Job(object):
    """No-op job"""
    def __init__(self, arguments):
        self.arguments = arguments

    def do(self):
        return self.arguments


class SimpleJob(Job):
    """Take a user-provided function to do the work, store args and result

    NOTE that this is a helper, first you must use functools.partial to
    create a partially bound Job using where work_fn:

    import functools
    Job = functools.partial(SimpleJob, your_work_fn)
    ...
    ...=Manager(Job, <tbl>)  # pass in your Job, not SimpleJob
    ..."""
    def __init__(self, work_fn, arguments):
        self.arguments = arguments
        self.work_fn = work_fn

    def do(self):
        return {"result": self.work_fn(self.arguments), "arguments": self.arguments}


def make_simple_job(work_fn):
    """Create a partial SimpleJob (convenience method)"""
    return partial(SimpleJob, work_fn)


class Manager(object):
    """Manage how jobs are run"""
    def __init__(self, job_prototype, tbl_prefix="default"):
        self.job_prototype = job_prototype
        self.tbl_prefix = tbl_prefix
        self.job_table = "jobs_" + self.tbl_prefix
        self.db_conn = config.get_db_connection()
        sqlite_utilities.make_table(self.job_table, self.db_conn)

    def add_job(self, arguments):
        return sqlite_utilities.add_job(self.job_table, arguments, self.db_conn)

    def get_available_job(self):
        return sqlite_utilities.get_available_job(self.job_table, self.db_conn)

    def count_job_states(self):
        return sqlite_utilities.count_job_states(self.job_table, self.db_conn)

    def completed_jobs(self, job_status=sqlite_utilities.JOB_STATUS_SUCCEEDED):
        """Return a generator of completed jobs"""
        return sqlite_utilities.get_results(self.job_table, job_status, self.db_conn)

    def do_single_job(self):
        job_id, arguments = self.get_available_job()
        try:
            print("do_single_job running with", arguments)
            job = self.job_prototype(arguments)
            result = job.do()
            sqlite_utilities.change_job_status(self.job_table, job_id, sqlite_utilities.JOB_STATUS_SUCCEEDED, self.db_conn, result=result)
        except Exception as err:
            sqlite_utilities.change_job_status(self.job_table, job_id, sqlite_utilities.JOB_STATUS_FAILED, self.db_conn, result=str(err))


class ProcessJobsInSeries(object):
    def __init__(self, manager):
        self.manager = manager

    def process(self, stop_when_all_jobs_completed=True):
        while True:
            try:
                from thread import get_ident
                import multiprocessing
                config.logging.info("Doing job on thread:" + str(get_ident()) + " " + str(multiprocessing.current_process()))
                self.manager.do_single_job()
            except job_exceptions.NoJobsException:
                if stop_when_all_jobs_completed:
                    break


class ProcessJobsInParallel(object):
    def __init__(self, manager, nbr_processes=2):
        self.manager = manager
        from multiprocessing import Process
        # note we can't use threading here as the sqlite interface isn't
        # thread-safe, we'd need multiple manager objects for this (TODO later)
        #from multiprocessing.dummy import Process
        self.job_processors = []
        self.processes = []
        for processor_nbr in range(nbr_processes):
            processor = ProcessJobsInSeries(manager)
            self.job_processors.append(processor)
            self.processes.append(Process(target=processor.process))

    def process(self, stop_when_all_jobs_completed=True):
        for p in self.processes:
            p.start()
        for p in self.processes:
            p.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Project description')
    #parser.add_argument('positional_arg', help='required positional argument')
    #parser.add_argument('--optional_arg', '-o', help='optional argument', default="Ian")

    args = parser.parse_args()
    print("These are our args:")
    print(args)
    #print("{} {}".format(args.positional_arg, args.optional_arg))

    config.logging.info("This is an example log message")

    mgr = Manager(Job)
