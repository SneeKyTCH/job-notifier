#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from job_notifier import SCRAPERS

for name, fn in SCRAPERS:
    jobs = fn()
    msg = f"{name}: {len(jobs)} joburi"
    if jobs:
        msg += f"  |  Ex: {jobs[0]['title'][:50]}"
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()
