# -*- coding: utf-8 -*-
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from mapreport import Report


class Test(unittest.TestCase):
    def test_report(self):
        __file__path = os.path.dirname(__file__)
        report = Report(
            os.path.join(__file__path, 'demo.map'),
            os.path.join(__file__path, 'config.yaml'),
            __file__path
        )
        report.generate_report()


if __name__ == '__main__':
    unittest.main()
