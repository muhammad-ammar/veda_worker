
import os
from setuptools import setup
from setuptools.command.install import install

def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='veda_worker',
    version='1.0',
    description='Node worker for VEDA',
    long_description=readme(),
    url='http://github.com/yro/veda_worker',
    author='@yro',
    author_email='greg@willowgrain.io',
    license='',
    packages=['veda_worker'],
    # scripts=['bin/veda_worker'],
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.yaml'],
    },
    install_requires=[
        'boto==2.39.0',
        'requests==2.10.0',
        'celery==3.1.18',
        'pyyaml==3.11',
        'nose==1.3.3',
        'newrelic'
    ],
    zip_safe=False
    )
