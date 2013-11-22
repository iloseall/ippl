#
# Copyright (C) 2013 Emerson Max de Medeiros Silva
#
# This file is part of lib2dipp.
#
# lib2dipp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lib2dipp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lib2dipp.  If not, see <http://www.gnu.org/licenses/>.
#

from lib2dipp.util import *
from lib2dipp.shape.base import Object


class Point(Object):

    def __init__(self, *args, **kwargs):
        """Creates a Point object.

        Parameters:
            args[0] a real number for x.
            args[1] a real number for y.
            OR
            kwargs["x"] a real number for x.
            kwargs["y"] a real number for y.
        """

        super(Point, self).__init__()

        x, y = self._parse_args(*args, **kwargs)
        self._x = x
        self._y = y

    def _parse_args(self, *args, **kwargs):
        values = [0.0, 0.0]
        if args:
            for i in range(len(args)):
                values[i] = float(args[i])
        elif kwargs:
            values[0] = float(kwargs.get("x", values[0]))
            values[1] = float(kwargs.get("y", values[1]))

        return values

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = float(value)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = float(value)

    def position(self, *args, **kwargs):
        x, y = self._parse_args(*args, **kwargs)
        self.x = x
        self.y = y

    def move(self, *args, **kwargs):
        x, y = self._parse_args(*args, **kwargs)
        self.x += x
        self.y += y

    def distance(self, point):
        return math.sqrt((point.x - self.x) * (point.x - self.x) +
            (point.y - self.y) * (point.y - self.y))

    def intersect_point(self, point):
        return self == point

    def intersect_rectangle(self, rectangle):
        return rectangle.intersect_point(self)

    def intersect_polygon(self, polygon):
        """Checks whether a point is inside a polygon.

        Parameters:
            polygon a list of Primitives.
        Return:
            True if the point is inside the polygon, or False otherwise.
        """

        odd_nodes = False
        polygon_size = len(polygon)

        for primitive in polygon:
            if isinstance(primitive, Line):
                line = primitive
                if ((line.y2 < self.y and line.y1 >= self.y) or
                        line.y1 < self.y and line.y2 >= self.y):
                    x_value = (line.x2 + (self.y - line.y2) /
                        (line.y1 - line.y2) * (line.x1 - line.x2))
                    if x_value < self.x:
                        odd_nodes = not odd_nodes
            elif isinstance(primitive, Arc):
                arc = primitive
                horizontal_line = Line(self, Point(self.x - 1, self.y))
                points = (
                    horizontal_line.calculate_intersection_circle_points(arc))

                if len(points) > 1:
                    for point in points:
                        angle = wrap_2pi(
                            math.atan2(point.y - arc.centre_point.y,
                                       point.x - arc.centre_point.x))
                        start = arc.start_angle
                        end = arc.offset_angle
                        if (angle_in_range(angle, start, end)):
                            if point.x < self.x:
                                odd_nodes = not odd_nodes

        return odd_nodes

    def collinear(self, line):
        cross_product = ((self.y - line.y1) * (line.x2 - line.x1) -
            (self.x - line.x1) * (line.y2 - line.y1))

        return not (abs(cross_product) > epsilon)

    def __getitem__(self, index):
        return (self.x, self.y)[index]

    def __eq__(self, point):
        return (approx_equal(self.x, point.x) and approx_equal(self.y, point.y))

    def __str__(self):
        return "{} ({}, {})".format(type(self).__name__, self.x, self.y)

    def __repr__(self):
        return "<{}>".format(self)

from lib2dipp.shape.line import Line
from lib2dipp.shape.arc import Arc