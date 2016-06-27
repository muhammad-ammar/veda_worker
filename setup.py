
import os
from setuptools import setup
from setuptools.command.install import install

def readme():
    with open('README.rst') as f:
        return f.read()


class FFInstall(install):
    """
    Should drop a compiled version of ffmpeg into this without too much hassle

    NOTE : this bin won't run reliably on most systems, so I'm including instructions to compile ffmpeg
    in the readme
    **
    """
    def run(self):
        install.run(self)
        os.system('wget http://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz')
        os.system('tar -xf ffmpeg-release-64bit-static.tar.xz')


setup(
    name='openveda',
    version='0.1',
    description='Single stream video encode for openedx',
    long_description=readme(),
    url='http://github.com/yro/openveda',
    author='@yro',
    author_email='greg@edx.org',
    license='',
    packages=['openveda'],
    install_requires=[
        'boto',
        'requests',
        'pysftp',
    ],
    ## dependency_links=['http://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz'],
    ## cmdclass={'install': FFInstall},
    zip_safe=False
    )
