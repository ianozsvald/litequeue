

    $ CONFIG=testing nosetests

To see stdout and let log.log contain some logging, use:

    $ CONFIG=testing nosetests -s --nologcapture


TODO
----

 * cleanup the multiprocessing/thread debug output (tests and job_queue)
 * build a multithreaded processor as an option
