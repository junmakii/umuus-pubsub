
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def run_tests(self):
        import sys
        import shlex
        import pytest
        errno = pytest.main(['--doctest-modules'])
        if errno != 0:
            raise Exception('An error occured during installution.')
        install.run(self)


setup(
    packages=setuptools.find_packages('.'),
    version='0.1',
    url='https://github.com/junmakii/umuus-pubsub',
    author='Jun Makii',
    author_email='junmakii@gmail.com',
    keywords=[],
    license='GPLv3',
    scripts=[],
    install_requires=['attrs>=18.2.0',
 'addict>=2.2.0',
 'fire>=0.1.3',
 'redis>=3.0.1',
 'toolz>=0.9.0'],
    dependency_links=[],
    classifiers=[],
    entry_points={'console_scripts': ['umuus_pubsub = umuus_pubsub:main'], 'gui_scripts': []},
    project_urls={},
    setup_requires=[],
    test_suite='',
    tests_require=[],
    extras_require={},
    package_data={},
    python_requires='',
    include_package_data=True,
    zip_safe=True,
    download_url='',
    name='umuus-pubsub',
    description='A simple Pub/Sub utility for Python.',
    long_description=('A simple Pub/Sub utility for Python.\n'
 '\n'
 'umuus-pubsub\n'
 '============\n'
 '\n'
 'Installation\n'
 '------------\n'
 '\n'
 '    $ pip install git+https://github.com/junmakii/umuus-pubsub.git\n'
 '\n'
 'Example\n'
 '-------\n'
 '\n'
 '    $ umuus_pubsub\n'
 '\n'
 '    >>> import umuus_pubsub\n'
 '\n'
 '----\n'
 '\n'
 '    $ cat REDIS.json\n'
 '    {\n'
 '        "host": "localhost",\n'
 '        "port": 6379,\n'
 '        "password": "..."\n'
 '    }\n'
 '\n'
 '    $ export REDIS_CONFIG_FILE=REDIS.json\n'
 '\n'
 '    $ python -m umuus_pubsub run --module MODULE\n'
 '\n'
 '----\n'
 '\n'
 "    umuus_pubsub.default.subscribe('foo').wait()  # wait until return a "
 'message\n'
 "    umuus_pubsub.default.publish('foo', 'bar')  # publish a message\n"
 '\n'
 '----\n'
 '\n'
 '    @umuus_pubsub.default.register()\n'
 '    def f(x):\n'
 '        print(x)\n'
 '        return x * x\n'
 '\n'
 "    umuus_pubsub.default.register(f, channel='test_channel_name')\n"
 '\n'
 '    umuus_pubsub.default.run()\n'
 '\n'
 '----\n'
 '\n'
 "    for message in umuus_pubsub.default.subscribe('*').gen():\n"
 '        print(message)\n'
 '\n'
 '----\n'
 '\n'
 '    async def f():\n'
 "        async for message in default.subscribe('*').async_gen():\n"
 '            print(message)\n'
 '\n'
 '    asyncio.run(f())\n'
 '\n'
 '----\n'
 '\n'
 'Authors\n'
 '-------\n'
 '\n'
 '- Jun Makii <junmakii@gmail.com>\n'
 '\n'
 'License\n'
 '-------\n'
 '\n'
 'GPLv3 <https://www.gnu.org/licenses/>'),
    cmdclass={"pytest": PyTest},
)
