=======
litequeue
=========

Batteries-included lightweight queueing module using sqlite3


Usage
-----

    litequeue $ python -m litequeue.admin  # show broken jobs, reset their state

    $ python get_twitter_profiles.py  # get profiles that we'd added

Tests
-----

    $ CONFIG=testing nosetests

To see stdout and let log.log contain some logging, use:

    $ CONFIG=testing nosetests -s --nologcapture




TODO
----

 * what is this for?
 * what's a minimal example?
 * cleanup the multiprocessing/thread debug output (tests and job_queue)
 * build a multithreaded processor as an option
 * investigate http://flask.pocoo.org/snippets/88/
