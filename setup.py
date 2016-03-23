from distutils.core import setup

import ast
import re
import sys

from setuptools import find_packages
from setuptools import setup

version = 0.1

setup(
    name='doing',
    version=version,

    author='meatpuppet',

    packages=['doing_pkg', 'doing_pkg.cli'],
    include_package_data=True,
    zip_safe=False,

    platforms='any',

    install_requires=[
        'python-dateutil',
        'humanize',
    ],


    entry_points={
        'console_scripts': ['doing=doing_pkg.__main__:main']
    },

    #description='Decentralised, minimalist microblogging service for hackers.',
    #long_description=open('./README.rst', 'r', encoding='utf-8').read(),

    keywords=[],

    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Communications',
        'Topic :: Utilities',
    ],
)