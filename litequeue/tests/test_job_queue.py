#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for start_here"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import unittest
import os
from litequeue import job_queue
from litequeue import job_exceptions
from litequeue import config
from litequeue.tests import fixtures
from litequeue import sqlite_utilities


def assert_we_are_using_testing_configuration():
    #assert config.db_filename == ":memory:"
    assert config.db_filename == "tests/testing_db.sqlite"
    try:
        os.remove(config.db_filename)
    except OSError:
        pass  # we don't care if the file wasn't already there


class Test(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.mgr = job_queue.Manager(job_queue.Job)

    def tearDown(self):
        sqlite_utilities.drop_table(self.mgr.job_table, self.mgr.db_conn)

    def test_adding_a_first_job(self):
        # make sure table has 0 jobs
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        # add job
        self.mgr.add_job(fixtures.job1_arguments)
        # make sure the queue has 1 job
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 1)
        self.assertEqual(nbr_in_process, 0)

        job_id, arguments = self.mgr.get_available_job()
        self.assertEqual(arguments, fixtures.job1_arguments)

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 1)
        self.assertEqual(nbr_succeeded, 0)
        self.assertEqual(nbr_failed, 0)

        c = self.mgr.db_conn.cursor()
        sqlite_utilities.mark_job_in_process(self.mgr.job_table, job_id, sqlite_utilities.JOB_STATUS_SUCCEEDED, self.mgr.db_conn, c)
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_succeeded, 1)
        self.assertEqual(nbr_failed, 0)

    def test_error_on_0_jobs(self):
        # make sure table has 0 jobs
        count_of_jobs = self.mgr.count_job_states()
        nbr_jobs = sum(count_of_jobs)
        self.assertEqual(nbr_jobs, 0)
        # try to get a non-existant job, check correct exception is raised
        self.assertRaises(job_exceptions.NoJobsException, self.mgr.get_available_job)

    def test_adding_and_process_job(self):
        # make sure table has 0 jobs
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        # add job
        self.mgr.add_job(fixtures.job1_arguments)
        # make sure the queue has 1 job
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 1)
        self.assertEqual(nbr_in_process, 0)

        self.mgr.do_single_job()

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_succeeded, 1)
        self.assertEqual(nbr_failed, 0)

        for job_id, result in self.mgr.completed_jobs():
            self.assertEqual(result, fixtures.job1_arguments)


class TestCrashingJob(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.mgr = job_queue.Manager(fixtures.JobAlwaysCrashes)

    def tearDown(self):
        sqlite_utilities.drop_table(self.mgr.job_table, self.mgr.db_conn)

    def test_adding_and_process_job_that_crashes(self):
        # make sure table has 0 jobs
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        # add job
        self.mgr.add_job(fixtures.job1_arguments)
        # make sure the queue has 1 job
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 1)
        self.assertEqual(nbr_in_process, 0)

        self.mgr.do_single_job()

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_succeeded, 0)
        self.assertEqual(nbr_failed, 1)

        for job_id, result in self.mgr.completed_jobs(sqlite_utilities.JOB_STATUS_FAILED):
            self.assertEqual(result, fixtures.job_always_crashes_result)


class TestUnicodeJob(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.mgr = job_queue.Manager(fixtures.JobWithUnicode)

    def tearDown(self):
        sqlite_utilities.drop_table(self.mgr.job_table, self.mgr.db_conn)

    def test_adding_and_process_job_that_crashes(self):
        # make sure table has 0 jobs
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        # add job
        self.mgr.add_job(fixtures.job1_arguments)
        # make sure the queue has 1 job
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 1)
        self.assertEqual(nbr_in_process, 0)

        # confirm that a unicode string is correctly encoded to bytes before
        # going in to sqlite3
        result = u"blahé"
        sqlite_utilities.change_job_status(self.mgr.job_table, 1, sqlite_utilities.JOB_STATUS_SUCCEEDED, self.mgr.db_conn, result=result)

        # now reset the job and check that it is correctly processed
        sqlite_utilities.change_job_status(self.mgr.job_table, 1, sqlite_utilities.JOB_STATUS_AVAILABLE, self.mgr.db_conn, result=None)
        self.mgr.do_single_job()

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_succeeded, 1)
        self.assertEqual(nbr_failed, 0)

        for job_id, result in self.mgr.completed_jobs():
            self.assertEqual(result, fixtures.unicode_job_result)


class TestJob(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.job = job_queue.Job(fixtures.job1_arguments)

    def test1(self):
        result = self.job.do()
        self.assertEqual(result, fixtures.job1_arguments)


def simple_work_fn(args):
    return "This did some work on " + repr(args)


class TestSimpleJob(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        Job = job_queue.make_simple_job(simple_work_fn)
        self.job = Job(fixtures.simple_work_fn_arguments)

    def test1(self):
        result = self.job.do()
        self.assertEqual(result, fixtures.simple_work_fn_result)


class TestProcessorWithSerialJobs(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.mgr = job_queue.Manager(job_queue.Job)
        self.processor = job_queue.ProcessJobsInSeries(self.mgr)

    def tearDown(self):
        sqlite_utilities.drop_table(self.mgr.job_table, self.mgr.db_conn)

    def test1(self):
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        # add job
        self.mgr.add_job(fixtures.job1_arguments)
        self.mgr.add_job(fixtures.job1_arguments)
        # make sure the queue has 1 job
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 2)
        self.assertEqual(nbr_in_process, 0)

        self.processor.process()

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_succeeded, 2)
        self.assertEqual(nbr_failed, 0)


class TestProcessorWithParallelJobs(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        # TODO note that we need 2 managers if we use threads
        # (multiprocessing.dummy) below, due to the requirement not to use
        # threads with sqlite3 - this needs fixing
        self.manager1 = job_queue.Manager(fixtures.JobWithSleep)
        self.manager2 = job_queue.Manager(fixtures.JobWithSleep)

    def tearDown(self):
        sqlite_utilities.drop_table(self.manager1.job_table, self.manager1.db_conn)

    def test1(self):
        processor1 = job_queue.ProcessJobsInSeries(self.manager1)
        processor2 = job_queue.ProcessJobsInSeries(self.manager2)

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = processor1.manager.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        NBR_JOBS = 11
        [processor1.manager.add_job((n,)) for n in xrange(NBR_JOBS)]
        # make sure the second processor can see the jobs put on by the first
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = processor2.manager.count_job_states()
        self.assertEqual(nbr_available, NBR_JOBS)
        self.assertEqual(nbr_in_process, 0)

        #from multiprocessing.dummy import Process
        from multiprocessing import Process
        p1 = Process(target=processor1.process)
        p2 = Process(target=processor2.process)
        p1.start()
        p2.start()
        p1.join()
        p2.join()

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = processor1.manager.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_failed, 0)
        self.assertEqual(nbr_succeeded, NBR_JOBS)

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = processor2.manager.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_failed, 0)
        self.assertEqual(nbr_succeeded, NBR_JOBS)


class TestProcessorWithParallelJobs2(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.manager1 = job_queue.Manager(fixtures.JobWith1SecondSleep)
        self.nbr_processes = 10
        self.parallel_processor = job_queue.ProcessJobsInParallel(self.manager1, nbr_processes=self.nbr_processes)

    def tearDown(self):
        sqlite_utilities.drop_table(self.manager1.job_table, self.manager1.db_conn)

    def test1(self):
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.parallel_processor.manager.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        # add 10 jobs
        NBR_JOBS = 30
        [self.parallel_processor.manager.add_job((n,)) for n in xrange(NBR_JOBS)]

        self.parallel_processor.process()

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.parallel_processor.manager.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_failed, 0)
        self.assertEqual(nbr_succeeded, NBR_JOBS)

        pids = set()
        for result in self.manager1.completed_jobs():
            print(result)
            pid = result[1]['worker pid']
            pids.add(pid)
        self.assertEqual(len(pids), self.nbr_processes)


if __name__ == "__main__":
    unittest.main()
