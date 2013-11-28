

    $ CONFIG=testing nosetests

To see stdout and let log.log contain some logging, use:

    $ CONFIG=testing nosetests -s --nologcapture


TODO
----

 * cleanup the multiprocessing/thread debug output (tests and job_queue)
 * build a multithreaded processor as an option
 * improve setup.py so it actually works!
 * investigate http://flask.pocoo.org/snippets/88/
