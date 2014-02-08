=======
litequeue
=========

Lightweight job queue using Python's built-in sqlite3 module (no other dependencies).

This is good for lightweight queue situations where you have 1000s of jobs that you'd like to run (in series, threaded or multiprocessed) backed by a persistent store to disk.

This is not meant to replace heavier-weight queues, this is for ad-hoc usage (I wrote it to help my data science clients with short research projects).

Usage
-----

* Create a worker function that takes 1 argument (it will receive a dictionary of your input arguments)
* Create a `job_queue.Manager` that knows about this function (see the example below)
* Create a `job_queue.ProcessJobsInSeries` that knows about the manager
* Add jobs to the processor
* Ask the processor to start processing
* Retrieve the completed jobs once finished

Exceptions raised in your worker function are pickled into the database and the job's flag is set to `sqlite_utilities.JOB_STATUS_FAILED` rather than `sqlite_utilities.JOB_STATUS_SUCCEEDED`. You can reset this flag (TODO).

Example
-------

Examples live in `litequeue\examples`.

OpenCorporates.org provide an API to company registration databases. Using a RESTful call to `http://api.opencorporates.com/companies/gb/<id_nbr>` we can retrieve the records for UK registered companies. The bulk of the code is:

```
def call_opencorporates(arguments):
    """Create URL, extract JSON from the result"""
    return requests.get(OPEN_CORPORATES_URL + arguments['id']).json()

manager = job_queue.Manager(job_queue.make_simple_job(call_opencorporates))
processor = job_queue.ProcessJobsInSeries(manager)
manager.add_job({'id': '08879300'})  # add a job as a dict of arguments to the queue
processor.process()  # process the queue of jobs
```

This example lives in `examples\call_opencorporates.py`:

```
examples $ python call_opencorporates.py --fetch 08879300 08879301
These are our args:
Namespace(fetch=['08879300', '08879301'])
Before processing:
JobStateCounts(NbrAvailable=2, NbrInProcess=0, NbrSucceeded=0, NbrFailed=0)
Now to process...
do_single_job running with {u'id': '08879300'}
do_single_job running with {u'id': '08879301'}
After processing:
JobStateCounts(NbrAvailable=0, NbrInProcess=0, NbrSucceeded=2, NbrFailed=0)  # manager.count_job_states()

Results:  # iterate over manager.completed_jobs()
(1, {u'result': {u'results': {u'company': {u'dissolution_date': None, u'branch_status': None, u'corporate_groupings': [], u'retrieved_at': None, u'updated_at': u'2014-02-06T10:11:27+00:00', u'industry_codes': [], u'inactive': False, u'registered_address_in_full': u'142D CHEETHAM HILL ROAD, MANCHESTER, ENGLAND, M8 8PZ', u'incorporation_date': u'2014-02-06', u'jurisdiction_code': u'gb', u'opencorporates_url': u'https://opencorporates.com/companies/gb/08879300', u'officers': [], u'previous_names': None, u'source': {u'url': u'http://xmlgw.companieshouse.gov.uk/', u'publisher': u'UK Companies House', u'terms': u'UK Crown Copyright', u'retrieved_at': None}, u'filings': [], u'company_type': u'Private Limited Company', u'data': None, u'name': u'INFLUENCE MARKETING & PROMOTION LTD', u'created_at': u'2014-02-06T10:11:27+00:00', u'company_number': u'08879300', u'current_status': u'Active', u'registry_url': u'http://data.companieshouse.gov.uk/doc/company/08879300'}}, u'api_version': u'0.2'}, u'arguments': {u'id': '08879300'}})
(2, {u'result': {u'results': {u'company': {u'dissolution_date': None, u'branch_status': None, u'corporate_groupings': [], u'retrieved_at': None, u'updated_at': u'2014-02-06T10:11:28+00:00', u'industry_codes': [], u'inactive': False, u'registered_address_in_full': u'FLAT 122, 100 WESTMINSTER BRIDGE ROAD, LONDON, UNITED KINGDOM, SE1 7XB', u'incorporation_date': u'2014-02-06', u'jurisdiction_code': u'gb', u'opencorporates_url': u'https://opencorporates.com/companies/gb/08879301', u'officers': [], u'previous_names': None, u'source': {u'url': u'http://xmlgw.companieshouse.gov.uk/', u'publisher': u'UK Companies House', u'terms': u'UK Crown Copyright', u'retrieved_at': None}, u'filings': [], u'company_type': u'Private Limited Company', u'data': None, u'name': u'FUDA LIMITED', u'created_at': u'2014-02-06T10:11:28+00:00', u'company_number': u'08879301', u'current_status': u'Active', u'registry_url': u'http://data.companieshouse.gov.uk/doc/company/08879301'}}, u'api_version': u'0.2'}, u'arguments': {u'id': '08879301'}})
```


Tests
-----

    $ CONFIG=testing nosetests

To see stdout and let log.log contain some logging, use:

    $ CONFIG=testing nosetests -s --nologcapture

To generate coverage information:

    $ CONFIG=testing nosetests --with-coverage --cover-html

You should also look at
-----------------------

If you want a heavier queue system then take a look at:

    * 0MQ https://github.com/zeromq/pyzmq
    * Celery http://www.celeryproject.org/
    * NSQ http://bitly.github.io/nsq/
    * Gearman http://gearman.org/

TODO
----

 * cleanup the multiprocessing/thread debug output (tests and job_queue)
 * build a multithreaded processor as an option
 * investigate http://flask.pocoo.org/snippets/88/
