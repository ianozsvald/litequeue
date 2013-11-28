#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for start_here"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
import cPickle
import config
import job_exceptions


JOB_STATUS_AVAILABLE = 0
JOB_STATUS_IN_PROCESS = 1
JOB_STATUS_SUCCEEDED = 2
JOB_STATUS_FAILED = 3


#def get_cursor(make_dict=False):
    #c = config.db_conn.cursor()
    #return c

def get_cursor():
    #db_conn = config.get_db_conn()
    db_conn = config.db_conn
    c = db_conn.cursor()
    return db_conn, c


def make_table(service):
    #c = get_cursor()
    db_conn, c = get_cursor()
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS {}
                (id integer primary key AUTOINCREMENT, status integer not null, arguments text, result text)'''.format(service))
    #config.db_conn.commit()
    db_conn.commit()


def count_jobs(service):
    sql = "SELECT COUNT(*) FROM {}".format(service)
    #c = get_cursor()
    db_conn, c = get_cursor()
    c.execute(sql)
    res = c.fetchone()
    return res[0]


def count_job_states_for_status(service, status_nbr):
    sql = "SELECT COUNT(*) FROM {} WHERE status=?".format(service)
    #c = get_cursor()
    db_conn, c = get_cursor()
    c.execute(sql, (status_nbr,))
    res = c.fetchone()
    return res[0]


def count_job_states(service):
    nbr_available = count_job_states_for_status(service, JOB_STATUS_AVAILABLE)
    nbr_in_process = count_job_states_for_status(service, JOB_STATUS_IN_PROCESS)
    nbr_succeeded = count_job_states_for_status(service, JOB_STATUS_SUCCEEDED)
    nbr_failed = count_job_states_for_status(service, JOB_STATUS_FAILED)
    return nbr_available, nbr_in_process, nbr_succeeded, nbr_failed


def add_job(service, arguments):
    pickled_arguments = cPickle.dumps(arguments)
    #c = get_cursor()
    db_conn, c = get_cursor()
    sql = "INSERT INTO {} (status, arguments, result) VALUES (?, ?, ?)".format(service)
    c.execute(sql, (JOB_STATUS_AVAILABLE, pickled_arguments, ""))
    #config.db_conn.commit()
    db_conn.commit()


def get_result(service, job_status):
    sql = "SELECT * FROM {} WHERE status=?".format(service)
    #c = get_cursor(True)
    db_conn, c = get_cursor()
    c.execute(sql, (job_status,))
    res = c.fetchone()
    result = cPickle.loads(str(res[b'result']))
    return res[b'id'], result


def change_job_status(service, job_id, new_status, result=None):
    #c = get_cursor(True)
    db_conn, c = get_cursor()
    if result:
        pickled_result = cPickle.dumps(result)
        sql = "UPDATE {} SET status=?, result=? WHERE id=?".format(service)
        c.execute(sql, (new_status, pickled_result, job_id))
    else:
        sql = "UPDATE {} SET status=? WHERE id=?".format(service)
        c.execute(sql, (new_status, job_id))
    db_conn.commit()


def get_available_job(service):
    #c = get_cursor(True)
    db_conn, c = get_cursor()
    sql = "SELECT * FROM {} WHERE status=?".format(service)
    c.execute(sql, (JOB_STATUS_AVAILABLE,))
    res = c.fetchone()
    if res is None:
        raise job_exceptions.NoJobsException()
    unpickled_arguments = cPickle.loads(str(res[b'arguments']))

    # TODO this should be an exclusive transaction?!

    job_id = res[b'id']
    change_job_status(service, job_id, JOB_STATUS_IN_PROCESS)

    return job_id, unpickled_arguments


def drop_table(service):
    db_conn, c = get_cursor()
    #c = get_cursor()
    c.execute('''DROP TABLE IF EXISTS {}'''.format(service))
    #config.db_conn.commit()
    db_conn.commit()
