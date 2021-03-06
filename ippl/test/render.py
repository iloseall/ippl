#
# Copyright (C) 2013-2014 Emerson Max de Medeiros Silva
#
# This file is part of ippl.
#
# ippl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ippl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ippl.  If not, see <http://www.gnu.org/licenses/>.
#

import math

from ippl.shape import *
from ippl.render import *

if __name__ == "__main__":
    s = Shape()
    # IV - Lines
    l = Line(Point(0, 0), Point(50, 25))
    s.outer_loop.append(l)
    l = Line(Point(50, 25), Point(0, 0))
    l.move(0, 30)
    s.outer_loop.append(l)
    l = Line(Point(0, 25), Point(50, 0))
    l.move(55, 0)
    s.outer_loop.append(l)
    l = Line(Point(50, 0), Point(0, 25))
    l.move(55, 30)
    s.outer_loop.append(l)

    aabb = s.bounds()
    size = aabb.size()
    size = (int(size[0]) + 1, int(size[1]) + 1)
    r = Render()
    r.draw_bounds = True
    r.image_size = size
    r.initialize()
    r.shape(s)
    r.save("render_test.png")

