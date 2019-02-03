
umuus-pubsub
============

Installation
------------

    $ pip install git+https://github.com/junmakii/umuus-pubsub.git

Example
-------

    $ umuus_pubsub

    >>> import umuus_pubsub

----

    $ cat REDIS.json
    {
        "host": "localhost",
        "port": 6379,
        "password": "..."
    }

    $ export REDIS_CONFIG_FILE=REDIS.json

    $ python -m umuus_pubsub run --module MODULE

----

    umuus_pubsub.default.subscribe('foo').wait()  # wait until return a message
    umuus_pubsub.default.publish('foo', 'bar')  # publish a message

----

    @umuus_pubsub.default.register()
    def f(x):
        print(x)
        return x * x

    umuus_pubsub.default.register(f, channel='test_channel_name')

    umuus_pubsub.default.run()

----

    for message in umuus_pubsub.default.subscribe('*').gen():
        print(message)

----

Authors
-------

- Jun Makii <junmakii@gmail.com>

License
-------

GPLv3 <https://www.gnu.org/licenses/>

Table of Contents
-----------------
.. toctree::
   :maxdepth: 2
   :glob:

   *

