#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for start_here"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import unittest
import job_queue
import job_exceptions
import config
import fixtures
import sqlite_utilities


def assert_we_are_using_testing_configuration():
    #assert config.db_filename == ":memory:"
    assert config.db_filename == "testing_db.sqlite"


class Test(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.mgr = job_queue.Manager(job_queue.Job)

    def tearDown(self):
        sqlite_utilities.drop_table(self.mgr.job_table)

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

        sqlite_utilities.change_job_status(self.mgr.job_table, job_id=job_id, new_status=sqlite_utilities.JOB_STATUS_SUCCEEDED)
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = self.mgr.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_succeeded, 1)
        self.assertEqual(nbr_failed, 0)

    def test_error_on_0_jobs(self):
        # make sure table has 0 jobs
        nbr_jobs = self.mgr.count_jobs()
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

        job_id, result = self.mgr.get_completed_job()
        self.assertEqual(result, fixtures.job1_arguments)


class TestCrashingJob(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.mgr = job_queue.Manager(fixtures.JobAlwaysCrashes)

    def tearDown(self):
        sqlite_utilities.drop_table(self.mgr.job_table)

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

        job_id, result = self.mgr.get_completed_job(sqlite_utilities.JOB_STATUS_FAILED)
        self.assertEqual(result, "division by zero")


class TestJob(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.job = job_queue.Job(fixtures.job1_arguments)

    def test1(self):
        result = self.job.do()
        self.assertEqual(result, fixtures.job1_arguments)


class TestProcessorWithSerialJobs(unittest.TestCase):
    def setUp(self):
        assert_we_are_using_testing_configuration()
        self.mgr = job_queue.Manager(job_queue.Job)
        self.processor = job_queue.ProcessJobsInSeries(self.mgr)

    def tearDown(self):
        sqlite_utilities.drop_table(self.mgr.job_table)

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
        self.manager1 = job_queue.Manager(fixtures.JobWithSleep)
        self.manager2 = job_queue.Manager(fixtures.JobWithSleep)

    def tearDown(self):
        sqlite_utilities.drop_table(self.manager1.job_table)
        pass

    def XXXtest1(self):
        processor1 = job_queue.ProcessJobsInSeries(self.manager1)
        processor2 = job_queue.ProcessJobsInSeries(self.manager2)

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = processor1.manager.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        # add 10 jobs
        [processor1.manager.add_job((n,)) for n in xrange(10)]
        # make sure the queue has 1 job via the second manager object
        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = processor2.manager.count_job_states()
        self.assertEqual(nbr_available, 10)
        self.assertEqual(nbr_in_process, 0)

        #from multiprocessing import Process
        from multiprocessing import dummy
        p1 = dummy.Process(target=processor1.process, args=())
        #p2 = Process(target=processor2.process)
        p1.start()
        #p2.start()
        p1.join()
        #p2.join()
        #processor1.process()
        #1/0

        nbr_available, nbr_in_process, nbr_succeeded, nbr_failed = processor2.manager.count_job_states()
        self.assertEqual(nbr_available, 0)
        self.assertEqual(nbr_in_process, 0)
        self.assertEqual(nbr_failed, 0)
        self.assertEqual(nbr_succeeded, 10)

if __name__ == "__main__":
    unittest.main()
