# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 11:39:17 2015

@author: geirb
"""

from so3spline import *
ex1 = {
'control_points': np.array([np.identity(3), np.array([[0.0,1,0], [-1,0,0], [0,0,1]]), np.array([[1.0,0,0],[0, 0, -1],[0,1,0]]), np.identity(3)]),
'knots': np.array([3.,3.,3.,4.,4.,4.])
}
b1 = BSpline(**ex1)
print(b1(3.5))
b1.plot()