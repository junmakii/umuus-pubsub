#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Jun Makii <junmakii@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""A simple Pub/Sub utility for Python.

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

"""
import sys
import copy
import json
import os
import types
import time
import threading
import toolz
import attr
import atexit
import functools
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=(__name__ == '__main__' and 'DEBUG' or
           os.environ.get(__name__.upper().replace('.', '__') + '_LOG_LEVEL')
           or os.environ.get('LOGGING_LOG_LEVEL') or 'DEBUG'),
    stream=sys.stdout)
logger.setLevel(
    __name__ == '__main__' and 'DEBUG'
    or os.environ.get(__name__.upper().replace('.', '__') + '_LOG_LEVEL')
    or os.environ.get('LOGGING_MODULE_LOG_LEVEL') or 'WARNING')logging_decorator = (lambda fn: functools.wraps(fn)(lambda *args, **kwargs: (lambda result: (logger.info((fn.__qualname__, args, kwargs)), result)[-1])(fn(*args, **kwargs))))
import redis
import fire
import attr
import addict
__version__ = '0.1'
__url__ = 'https://github.com/junmakii/umuus-pubsub'
__author__ = 'Jun Makii'
__author_email__ = 'junmakii@gmail.com'
__author_username__ = 'junmakii'
__keywords__ = []
__license__ = 'GPLv3'
__scripts__ = []
__install_requires__ = [
    'attrs>=18.2.0',
    'addict>=2.2.0',
    'fire>=0.1.3',
    'redis>=3.0.1',
]
__dependency_links__ = []
__classifiers__ = []
__entry_points__ = {
    'console_scripts': ['umuus_pubsub = umuus_pubsub:main'],
    'gui_scripts': [],
}
__project_urls__ = {}
__setup_requires__ = []
__test_suite__ = ''
__tests_require__ = []
__extras_require__ = {}
__package_data__ = {}
__python_requires__ = ''
__include_package_data__ = True
__zip_safe__ = True
__static_files__ = {}
__extra_options__ = {}
__download_url__ = ''
__all__ = []


@attr.s()
class Redis(object):
    env_name = attr.ib('REDIS_CONFIG_FILE')
    instance = None
    handlers = attr.ib(attr.Factory(dict))
    shared_state = type('State', (object, ), dict(is_running=False, ))()
    queue = attr.ib(attr.Factory(list))

    def connect(self):
        self.instance = redis.Redis(
            decode_responses=True,
            **json.load(open(os.environ.get(self.env_name))))
        self.shared_state.is_running = True
        return self

    def subscribe(self, patterns=[], handlers={}):
        self = copy.copy(self)
        self.queue = []
        logger.info('subscribe: ' + str((patterns, handlers)))
        self.pubsub = self.instance.pubsub()
        self.pubsub.psubscribe(*(
            isinstance(patterns, list) and patterns or [patterns]))
        handlers and self.pubsub.psubscribe(**handlers)
        threading.Thread(target=self.loop).start()
        return self

    def exit(self):
        self.shared_state.is_running = False

    @toolz.curry
    def register(self, fn, channel=None):
        channel = channel or (fn.__module__ + '.' + fn.__qualname__)
        logger.info('register: %s' % channel)

        def handler(message):
            if message and message['type'] in ['pmessage']:
                try:
                    metadata = addict.Dict(
                        zip(['name', 'event', 'id'], message['channel'].split(
                            ':', 2)))
                    data = self.serialize(message['data'])
                    result = (isinstance(data, dict) and fn(**data)
                              or fn(data))
                    self.instance.publish(
                        channel + ':completed:' + metadata.id,
                        self.normalize(result))
                except Exception as err:
                    self.instance.publish(channel + ':error:' + metadata.id,
                                          self.normalize(dict(error=err)))

        self.handlers.update({channel + ':next:*': handler})
        return fn

    def serialize(self, data):
        return (
            lambda _: toolz.excepts(Exception, json.loads, lambda err: _)(_)
        )(data)

    def normalize(self, data):
        return (
            lambda _: toolz.excepts(Exception, json.dumps, lambda err: str(_))(_)
        )(data)

    def publish(self, channel, message):
        self.instance.publish(channel, self.normalize(message))
        return self

    def wait(self):
        while self.shared_state.is_running and not self.queue:
            time.sleep(0.1)
        return self.serialize(self.queue.pop()['data'])

    def gen(self):
        while self.shared_state.is_running:
            yield self.wait()

    def loop(self):
        while self.shared_state.is_running:
            message = self.pubsub.get_message(ignore_subscribe_messages=True)
            if message and message['type'] in ['pmessage']:
                self.queue.insert(0, message)
            time.sleep(0.1)

    def close(self):
        self.shared_state.is_running = False

    def run(self):
        self = copy.copy(self)
        self.pubsub = self.instance.pubsub()
        self.pubsub.psubscribe(**self.handlers)
        self.pubsub.run_in_thread(sleep_time=0.1)


default = Redis().connect()


def from_modules(modules):
    fns = [
        attr for module_name in modules
        for module in [__import__(module_name)]
        for key, attr in vars(module).items()
        if isinstance(attr, types.FunctionType) and not key.startswith('_')
    ]
    print(fns)
    for fn in fns:
        default.register(fn)


def from_paths(paths):
    fns = [
        function for path in paths
        for module_name, function_name in [path.split(':')]
        for module in [__import__(module_name)]
        for function in [getattr(module, function_name)]
    ]
    for fn in fns:
        default.register(fn)


def run(options={}, **kwargs):
    options = addict.Dict(options, **kwargs)
    if options.modules:
        from_modules(options.modules)
    if options.module:
        from_modules([options.module])
    elif options.paths:
        from_paths(options.paths)
    elif options.path:
        from_paths([options.path])
    default.run()


def main(argv=None):
    fire.Fire()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
