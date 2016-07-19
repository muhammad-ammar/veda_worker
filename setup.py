
import os
from setuptools import setup
from setuptools.command.install import install

def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='veda_worker',
    version='0.1',
    description='Node worker for VEDA',
    long_description=readme(),
    url='http://github.com/yro/veda_worker',
    author='@yro',
    author_email='greg@willowgrain.io',
    license='',
    packages=['veda_worker'],
    install_requires=[
        'boto',
        'requests',
        'pysftp',
    ],
    zip_safe=False
    )
