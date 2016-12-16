
import numpy as np

from .geometry import Geometry
from . import BSpline

from padexp import Exponential

Exp = Exponential(order=16)

def exponential(xi):
    return Exp(xi)[0]

class Interpolator():
    max_iter = 500
    tolerance = 1e-12
    geometry = Geometry()

    def __init__(self, interpolation_points, boundary_velocities, geometry):
        self.interpolation_points = interpolation_points
        self.boundary_deformations = [1/3*geometry.connection(self.interpolation_points[j], boundary_velocities[i]) for i,j in ((0,0), (1,-1))]
        self.geometry = geometry
        self.size = len(self.interpolation_points)

    def compute_spline(self):
        """
        Produces a spline object.
        """
        deformations = self.compute_deformations()
        control_points = np.array(list(self.control_points(deformations)))
        spline_control_points = self.compute_spline_control_points(control_points)
        knots = np.arange(len(self.interpolation_points[0]), dtype='f').repeat(3)
        return BSpline(control_points=spline_control_points,
                       knots=knots,
                       geometry=self.geometry)


    def compute_deformations(self):
        """
        Compute the control points giving a C2 de Casteljau spline.
        """
        deformations = self.geometry.zero_deformations(self.interpolation_points)
        for i in range(self.max_iter):
            interior = self.interior_deformations(deformations)
            error = deformations[1:-1] - interior
            deformations[1:-1] = interior
            for i,j in ((0,0), (1,-1)):
                deformations[j] = self.boundary_deformations[i]
            if np.max(np.abs(error)) < self.tolerance:
                break
        else:
            raise Exception("No convergence in {} steps; error :{} ".format(i, error))
        return deformations

    def control_points(self, deformations, shift=1):
        """
        Compute the interior control points, from the given deformations.
        """
        N = self.size
        all_range = range(N)
        left_range = all_range[shift:]
        right_range = all_range[:-shift]
        g = self.geometry
        for l,r in zip(left_range, right_range):
            # left control point at i+1
            left = g.action(exponential(-deformations[l]), self.interpolation_points[l])
            # right control point at i-1
            right = g.action(exponential(deformations[r]), self.interpolation_points[r])
            yield right, left

    def interior_deformations(self, deformations):
        """
        Compute new deformations at interior points from old deformations.
        """
        N = self.size

        g = self.geometry

        interior_deformations = deformations[1:-1]
        sig_left = np.zeros_like(interior_deformations)
        sig_right = np.zeros_like(interior_deformations)

        for i, (P, d, (right, left)) in enumerate(zip(
                self.interpolation_points[1:-1],
                interior_deformations,
                self.control_points(deformations, shift=2))):
            pt_left = g.action(exponential(-d), left)
            sig_right[i] = g.redlog(P, pt_left)
            pt_right = g.action(exponential(d), right)
            sig_left[i] = g.redlog(P, pt_right)

        return (sig_right - sig_left + 2*interior_deformations)/4

    def compute_spline_control_points(self, control_points):
        """
        Produces a spline control points from the given control points
        in an array.
        """
        geo_shape = np.shape(self.interpolation_points[0])
        new_shape = (3*self.size-2,) + geo_shape
        all_points = np.zeros(new_shape)
        all_points[::3] = self.interpolation_points
        all_points[1::3] = control_points[:,0]
        all_points[2::3] = control_points[:,1]
        return all_points