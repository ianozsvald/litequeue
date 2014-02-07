#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cmd line demo to add jobs via RESTful web calls and showing the result

Pass in some UK Corporate ids for our code to fetch from the OpenCorporates
website, the retrieved JSON will be shown from the sqlite results:

    $ python call_opencorporates.py --fetch 08879300 08879301


or just call without fetch if you only want to see current results:

    $ python call_opencorporates.py

"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""
from functools import partial
import argparse
from litequeue import job_queue
import requests

OPEN_CORPORATES_URL = "http://api.opencorporates.com/companies/gb/{}"


def call_opencorporates(arguments):
    url = OPEN_CORPORATES_URL.format(arguments['id'])
    r = requests.get(url)
    return r.json()


manager = job_queue.Manager(partial(job_queue.SimpleJob, call_opencorporates))
processor = job_queue.ProcessJobsInSeries(manager)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Project description')
    parser.add_argument('--fetch', '-f', nargs='*', default=[], help='fetch from opencorporates')

    args = parser.parse_args()
    print("These are our args:")
    print(args)

    if args.fetch:
        for follower_id in args.fetch:
            manager.add_job({'id': str(follower_id)})

        print("Before processing:")
        print(manager.count_job_states())
        print("Now to process...")
        processor.process()
        print("After processing:")
        print(manager.count_job_states())

    print("\nResults:")
    for result in manager.completed_jobs():
        print(result)
