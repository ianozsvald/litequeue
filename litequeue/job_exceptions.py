#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for start_here"""
from __future__ import division  # 1/2 == 0.5, as in Py3
from __future__ import absolute_import  # avoid hiding global modules with locals
from __future__ import print_function  # force use of print("hello")
from __future__ import unicode_literals  # force unadorned strings "" to be unicode without prepending u""


class NoJobsException(Exception):
    pass
