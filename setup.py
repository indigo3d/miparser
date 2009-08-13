# -*- coding: utf-8 -*-
import ez_setup

ez_setup.use_setuptools()
from setuptools import setup
setup(
    name = "miparser",
    version = "0.1",
    packages=['miparser'],
    # entry_points = {
    #     'console_scripts': [
    #         'miparser = miparser:main',
    #         ],
    #     },
    install_requires = ['ply', 'odict']
    )
    
                

