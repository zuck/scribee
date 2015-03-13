#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This file is part of the Scribee project.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2011 Emanuele Bertoldi'
__version__ = '0.0.1'

def filter(block):
    block.filtered = '\n'.join([l.strip().replace('/*', "").replace("*/", "").strip(" *") for l in block.filtered.splitlines()])
