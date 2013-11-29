
Usage
-----

    $ python admin.py  # show broken jobs, reset their state

    $ python get_twitter_profiles.py  # get profiles that we'd added

Tests
-----

    $ CONFIG=testing nosetests

To see stdout and let log.log contain some logging, use:

    $ CONFIG=testing nosetests -s --nologcapture




TODO
----

 * cleanup the multiprocessing/thread debug output (tests and job_queue)
 * build a multithreaded processor as an option
 * improve setup.py so it actually works!
 * investigate http://flask.pocoo.org/snippets/88/
 * does an exception that contains unicode *not* get stored, as it hasn't been encoded to a plain string?