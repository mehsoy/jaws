#!/usr/bin/python
#-*- coding: utf-8 -*-

from setuptools import setup

setup(name='jaws',
    version='0.1.0',
    author=["Mehmet Soysal","Johann Mantel", "Jakob Ohm", "Adrian Beer", "Maximilian Beichter", "Anna Fedorchenko",
            "Dmytro Dehtyarov"],
    author_email=["mehmet.soysal@kit.edu", "j-mantel@gmx.net", "adrianbeer@fastmail.com", "maximilian.beichter@gmail.com", "dmytro.dehtyarov@gmail.com", "anna.o.fedorchenko@gmail.com", "jakob.ohm@protonmail.com"],
    url="https://git.scc.kit.edu/az2556/jaws",
    package_dir = {'': 'src'},
    packages=['application', 'controller', 'database', 'exceptions', 'master', 'views', 'worker','tests'],
    entry_points={'console_scripts': ['jaws = views.__main__:main',
                                      'dmdcontroller = controller.__main__:main',
                                      'dmdsearch = search.__main__:main',
                                      'dmdworker = worker.__main__:main']},)
