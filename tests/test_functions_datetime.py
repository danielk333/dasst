#!/usr/bin/env python

'''

'''

import sys
import os
sys.path.insert(0, os.path.abspath('.'))
import time

import unittest
import numpy as np
import numpy.testing as nt

import dasst.functions.datetime as dt


class TestTimes(unittest.TestCase):
    '''
    J2000: January 1, 2000, 11:58:55.816 UTC
    J2000: 2451545.0 JD
    MJD = JD - 2400000.5
    '''
    def test_yearday_to_monthday(self):

        pair = dpt.yearday_to_monthday(30.1, False)
        self.assertAlmostEqual(pair[0], 1.0)
        self.assertAlmostEqual(pair[1], 30.1)

        pair = dpt.yearday_to_monthday(31.1, False)
        self.assertAlmostEqual(pair[0], 1.0)
        self.assertAlmostEqual(pair[1], 31.1)

        pair = dpt.yearday_to_monthday(32.1, False)
        self.assertAlmostEqual(pair[0], 2.0)
        self.assertAlmostEqual(pair[1], 1.1)

        pair = dpt.yearday_to_monthday(60.1, False)
        self.assertAlmostEqual(pair[0], 3.0)
        self.assertAlmostEqual(pair[1], 1.1)

        pair = dpt.yearday_to_monthday(60.1, True)
        self.assertAlmostEqual(pair[0], 2.0)
        self.assertAlmostEqual(pair[1], 29.1)

        pair = dpt.yearday_to_monthday(90.1, False)
        self.assertAlmostEqual(pair[0], 3.0)
        self.assertAlmostEqual(pair[1], 31.1)

        pair = dpt.yearday_to_monthday(91.1, False)
        self.assertAlmostEqual(pair[0], 4.0)
        self.assertAlmostEqual(pair[1], 1.1)


    def test_date_to_jd_int(self):
        JD = dpt.date_to_jd(2000, 01, 01)

        JD_ref = 2451545.0 - 0.5
        
        self.assertAlmostEqual(JD, JD_ref)

    def test_date_to_jd_float(self):
        JD = dpt.date_to_jd(2000, 1, 1.5)

        JD_ref = 2451545.0
        
        self.assertAlmostEqual(JD, JD_ref)

    def test_jd_to_date_int(self):

        JD_ref = 2451545.0 - 0.5
        date = dpt.jd_to_date(JD_ref)

        date_ref = (2000, 1, 1)
        
        self.assertTupleEqual(date, date_ref)

    def test_jd_to_date_float(self):

        JD_ref = 2451545.0
        date = dpt.jd_to_date(JD_ref)

        date_ref = (2000, 1, 1.5)
        
        self.assertTupleEqual(date, date_ref)

    def test_jd_to_date_floor(self):
        dt = n.linspace(0,0.9,num=100)
        JD_ref = 2451545.0 - 0.5 + dt
        date_ref = n.array([2000, 1, 1.0], dtype=n.float)

        for JDi in range(len(JD_ref)):
            date = n.array(dpt.jd_to_date(JD_ref[JDi]), dtype=n.float)
            date_ref[2] = 1.0 + dt[JDi]
            nt.assert_almost_equal(date, date_ref, decimal=5)


    def test_gmst(self):
        '''Test J2000 gives correct hour angle.
        
        J2000: January 1, 2000, 11:58:55.816 UTC
        Reference for numerical values: Meeus, J., 2000. Astronomical Algorithms. Willman-Bell, Richmond,VA, 2nd ed. 
        '''
        
        JD = 2451545.0
        MJD = JD - 2400000.5

        ang = dpt.gmst(MJD)

        self.assertAlmostEqual(n.degrees(ang), 280.46061837)

        #linear growth, cyclic
        d_dt = (dpt.gmst(MJD + 1.0) - dpt.gmst(MJD))/1.0
        self.assertAlmostEqual(
            dpt.gmst(MJD + 3.0),
            n.mod(dpt.gmst(MJD) + 3.0*d_dt, 2.0*n.pi)
        )
    
    def test_gmst_numpy(self):
        x = n.linspace(1, 3, num=100, dtype=n.float)
        y = n.ones((100,10), dtype=n.float)

        v = dpt.gmst(x)
        self.assertEqual(v.shape, x.shape)

        v = dpt.gmst(y)
        self.assertEqual(v.shape, y.shape)


if __name__ == '__main__':
    unittest.main(verbosity=2)