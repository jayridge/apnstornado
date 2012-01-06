apnstornado
===========

apnstornado is a rest interface for apples push notification service.

To use this application you will need

 * [tornado](http://www.tornadoweb.org/)
 * [pylibmc](http://sendapatch.se/projects/pylibmc/)
 * A development and/or production pem
 * An installed 2048 entrust root cert

Before you being, check your certs by running test_the_pem.sh.

To run the suhva

    memcached -d
    python apns_server.py
