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

import math

from lib2dipp import util
from lib2dipp.shape.point import Point
from lib2dipp.shape.rectangle import Rectangle
from lib2dipp.shape.line import Line


class Arc(object):

    def __init__(self, centre_point=Point(), radius=1, start_angle=0,
            offset_angle=0):
        """Creates a Arc object.

        Parameters:
            centre_point a Point object.
            radius a real number.
            start_angle a real number.
            offset_angle a real number.
        """

        super(Arc, self).__init__()

        self.centre_point = centre_point
        self._radius = float(radius)
        self._start_angle = float(start_angle)
        self._offset_angle = float(offset_angle)
        self._line = Line()

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = float(value)

    @property
    def start_angle(self):
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = util.wrap_2pi(float(value))

    @property
    def offset_angle(self):
        return self._offset_angle

    @offset_angle.setter
    def offset_angle(self, value):
        self._offset_angle = util.wrap_2pi(float(value))

    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, value):
        self.line = value

    def position(self, x, y):
        point = Point(x, y)
        self.centre_point = point

    def move(self, x, y):
        self.centre_point.x += x
        self.centre_point.y += y

        self.line.move(x, y)

    def bounds(self):
        self.calculate_ends()

        start = self.start_angle
        end = self.offset_angle
        minimum_x, maximum_x, minimum_y, maximum_y = (
            self.centre_point.x - self.radius,
            self.centre_point.x + self.radius,
            self.centre_point.y - self.radius,
            self.centre_point.y + self.radius
        )

        if util.wrap_2pi(start) >= util.wrap_2pi(end):
            maximum_x = self.centre_point.x + self.radius
        else:
            maximum_x = max(self.line.x1, self.line.x2)
        if (util.wrap_2pi(start - util.pi / 2.0) >=
                util.wrap_2pi(end - util.pi / 2.0)):
            maximum_y = self.centre_point.y + self.radius
        else:
            maximum_y = max(self.line.y1, self.line.y2)

        if util.wrap_2pi(start - util.pi) >= util.wrap_2pi(end - util.pi):
            minimum_x = self.centre_point.x - self.radius
        else:
            minimum_x = min(self.line.x1, self.line.x2)
        if (util.wrap_2pi(start - 3.0 * util.pi / 2.0) >=
                util.wrap_2pi(end - 3.0 * util.pi / 2.0)):
            minimum_y = self.centre_point.y - self.radius
        else:
            minimum_y = min(self.line.y1, self.line.y2)

        return Rectangle(minimum_x, minimum_y, maximum_x, maximum_y)

    def intersect_line(self, line, ignore_alpha=False, ignore_beta=False):
        return line.intersect_arc(self, ignore_alpha, ignore_beta)

    def intersect_arc(self, arc):
        """Calculate the points between two arcs.

        Parameters:
            arc a Arc object.
        Return:
            A list of 0-2 points if the same are within the angle range of the
            arc. Or arc if the distance between the centers is 0 and radius are
            equal.
        """

        result = []
        p1 = self.centre_point
        start1 = self.start_angle
        end1 = self.offset_angle
        p2 = arc.centre_point
        start2 = arc.start_angle
        end2 = arc.offset_angle

        distance = p1.distance(p2)
        if (abs(arc.radius - self.radius) < distance <
                (self.radius + arc.radius)):
            points = self.calculate_intersection_circle_points(arc, distance)
            for point in points:
                angle1 = (
                    util.wrap_2pi(math.atan2(point.y - p1.y, point.x - p1.x)))
                angle2 = (
                    util.wrap_2pi(math.atan2(point.y - p2.y, point.x - p2.x)))

                if (util.angle_in_range(angle1, start1, end1) and
                        util.angle_in_range(angle2, start2, end2)):

                    result.append(point)
        elif (util.approx_equal(distance, 0.0) and
                util.approx_equal(self.radius, arc.radius)):
            result_arc = Arc(self.centre_point, self.radius)

            if util.angle_in_range(start1, start2, end2):
                result_arc.start_angle = self.start_angle
            elif util.angle_in_range(start2, start1, end1):
                result_arc.start_angle = arc.start_angle
            if util.angle_in_range(end1, start2, end2):
                result_arc.offset_angle = self.offset_angle
            elif util.angle_in_range(end2, start1, end1):
                result_arc.offset_angle = arc.offset_angle

            result = [result_arc]

        return result

    def calculate_ends(self):
        self.line.x1 = (self.centre_point.x +
            self.radius * math.cos(self.start_angle))
        self.line.y1 = (self.centre_point.y +
            self.radius * math.sin(self.start_angle))
        self.line.x2 = (self.centre_point.x +
            self.radius * math.cos(self.offset_angle))
        self.line.y2 = (self.centre_point.y +
            self.radius * math.sin(self.offset_angle))

    def calculate_angles(self):
        self.start_angle = util.wrap_2pi(
            math.atan2(self.line.y1 - self.centre_point.y,
                       self.line.x1 - self.centre_point.x))
        self.offset_angle = util.wrap_2pi(
            math.atan2(self.line.y2 - self.centre_point.y,
                       self.line.x2 - self.centre_point.x))

    def calculate_intersection_circle_points(self, circle, distance=None):
        """Calculate the points between two circles.

        Parameters:
            circle a Arc object.
            distance the distance between the center points of the circles, or
            None to calculate the distance.
        Return:
            A list with two points.
        """

        p1 = self.centre_point
        r1 = self.radius
        p2 = circle.centre_point
        r2 = circle.radius

        if not distance:
            distance = p1.distance(p2)

        a = ((r1 * r1) - (r2 * r2) + (distance * distance)) / (2 * distance)
        h = math.sqrt(r1 * r1 - a * a)
        s = a / distance
        p3 = Point(p1.x + s * (p2.x - p1.x), p1.y + s * (p2.y - p1.y))

        x3 = p3.x + h * (p2.y - p1.y) / distance
        y3 = p3.y - h * (p2.x - p1.x) / distance
        x4 = p3.x - h * (p2.y - p1.y) / distance
        y4 = p3.y + h * (p2.x - p1.x) / distance

        return [Point(x3, y3), Point(x4, y4)]

    def rounded(self):
        self.centre_point.rounded()
        radius = util.round_number(self.radius)
        start_angle = util.round_number(self.start_angle)
        offset_angle = util.round_number(self.offset_angle)
        return Arc(self.centre_point.rounded(), radius, start_angle,
            offset_angle)

    def __str__(self):
        return ("{} (\n"
                "  {}\n"
                "  centre_point={},\n"
                "  radius={:.20f},\n"
                "  start_angle={:.20f},\n"
                "  offset_angle={:.20f}\n"
                ")".format(type(self).__name__, str(self.line),
                           self.centre_point, self.radius, self.start_angle,
                           self.offset_angle))

    def __repr__(self):
        return "<{}>".format(self)