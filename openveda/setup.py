
import os
import sys
import subprocess
# import yaml

from setuptools import setup
from setuptools.command.install import install

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'ffmpeg_compiler'
        )
    )
from ffmpeg_compile import FFCompiler
# from openveda.ff_compile import FFInstall

def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='openveda',
    version='1.0',
    description='Single stream video encode for openedx',
    long_description=readme(),
    url='http://github.com/yro/openveda',
    author='@yro',
    author_email='greg@willowgrain.io',
    license='GNU',
    packages=['openveda'],
    install_requires=[
        'boto',
        'requests',
        'pyyaml',
        'nose',
        # 'vhls'
    ],
    scripts=['bin/openveda'],
    # cmdclass={'install': FFInstall},
    # ^^^^ Yeah, no dice
    zip_safe=False
    )

FF = FFCompiler()
if FF.check() is False:
    FF.run()

