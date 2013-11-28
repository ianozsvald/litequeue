#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for start_here"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import cPickle
from collections import namedtuple
import job_exceptions


JOB_STATUS_AVAILABLE = 0
JOB_STATUS_IN_PROCESS = 1
JOB_STATUS_SUCCEEDED = 2
JOB_STATUS_FAILED = 3


def make_table(service, db_conn):
    c = db_conn.cursor()
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS {}
                (id integer primary key AUTOINCREMENT, status integer not null, arguments text, result text)'''.format(service))
    db_conn.commit()


#def count_jobs(service, db_conn):
    #sql = "SELECT COUNT(*) FROM {}".format(service)
    #c = db_conn.cursor()
    #c.execute(sql)
    #res = c.fetchone()
    #return res[0]


def count_job_states_for_status(service, status_nbr, db_conn):
    sql = "SELECT COUNT(*) FROM {} WHERE status=?".format(service)
    c = db_conn.cursor()
    c.execute(sql, (status_nbr,))
    res = c.fetchone()
    return res[0]


def count_job_states(service, db_conn):
    nbr_available = count_job_states_for_status(service, JOB_STATUS_AVAILABLE, db_conn)
    nbr_in_process = count_job_states_for_status(service, JOB_STATUS_IN_PROCESS, db_conn)
    nbr_succeeded = count_job_states_for_status(service, JOB_STATUS_SUCCEEDED, db_conn)
    nbr_failed = count_job_states_for_status(service, JOB_STATUS_FAILED, db_conn)
    JobStateCounts = namedtuple("JobStateCounts", "NbrAvailable NbrInProcess NbrSucceeded NbrFailed")
    job_state_counts = JobStateCounts(nbr_available, nbr_in_process, nbr_succeeded, nbr_failed)
    return job_state_counts


def add_job(service, arguments, db_conn):
    pickled_arguments = cPickle.dumps(arguments)
    c = db_conn.cursor()
    c.execute("BEGIN IMMEDIATE")
    sql = "INSERT INTO {} (status, arguments, result) VALUES (?, ?, ?)".format(service)
    c.execute(sql, (JOB_STATUS_AVAILABLE, pickled_arguments, ""))
    db_conn.commit()


def get_result(service, job_status, db_conn):
    sql = "SELECT * FROM {} WHERE status=?".format(service)
    c = db_conn.cursor()
    c.execute(sql, (job_status,))
    res = c.fetchone()
    result = cPickle.loads(str(res[b'result']))
    return res[b'id'], result


def change_job_status(service, job_id, new_status, db_conn, result):
    c = db_conn.cursor()
    pickled_result = cPickle.dumps(result)
    sql = "UPDATE {} SET status=?, result=? WHERE id=?".format(service)
    c.execute(sql, (new_status, pickled_result, job_id))
    db_conn.commit()


def mark_job_in_process(service, job_id, job_status, db_conn, c):
    sql = "UPDATE {} SET status=? WHERE id=?".format(service)
    c.execute(sql, (job_status, job_id))
    db_conn.commit()


def get_available_job(service, db_conn):
    c = db_conn.cursor()
    # block the db from letting someone else see the same available job
    c.execute("BEGIN IMMEDIATE")
    sql = "SELECT * FROM {} WHERE status=?".format(service)
    c.execute(sql, (JOB_STATUS_AVAILABLE,))
    res = c.fetchone()
    if res is None:
        db_conn.commit()
        raise job_exceptions.NoJobsException()
    unpickled_arguments = cPickle.loads(str(res[b'arguments']))

    job_id = res[b'id']
    mark_job_in_process(service, job_id, JOB_STATUS_IN_PROCESS, db_conn, c)
    return job_id, unpickled_arguments


def drop_table(service, db_conn):
    c = db_conn.cursor()
    c.execute('''DROP TABLE IF EXISTS {}'''.format(service))
    db_conn.commit()
