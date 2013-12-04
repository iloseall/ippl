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

from lib2dipp.render import *
from lib2dipp.shape import *

if __name__ == "__main__":
    s = Shape()
    s.outer_loop.append(Line(Point(0, 100), Point(0, 0)))
    s.outer_loop.append(Line(Point(0, 0), Point(100, 0)))
    s.outer_loop.append(Line(Point(100, 0), Point(100, 100)))
    s.outer_loop.append(Line(Point(100, 100), Point(0, 100)))

    aabb = s.bounds()
    size = (int(aabb.right - aabb.left) + 1, int(aabb.top - aabb.bottom) + 1)
    r = Render()
    r.draw_bounds = True
    r.image_size = size
    r.shape(s)
    lp = s.lowest_point()
    r._image_drawer.point((lp.x, lp.y), (255, 0, 0))
    r.save("lowest_point.png")

    print lp
