#!/usr/bin/env python3
"""
FlowCore Pipeline Runner
========================
Executes the monitoring pipeline and outputs a formatted report.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flowcore.modules.watcher import run

if __name__ == "__main__":
    print(run())
