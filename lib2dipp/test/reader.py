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

import ast
import re
import sys

from lib2dipp.render import *


class StateMachine(object):
    STATES = {
        "profile": 1,
        "shape": 2,
        "loop": 3,
        "line": 4,
        "arc": 5,
        "end": 6
    }

    EXPRESSIONS = {
        "profile": re.compile(r"^Profiles(?P<id>\d+): (?P<size>\(\d+,\d+\)), "
                              r"Shapes: (?P<shapes>\d+), Rotations: "
                              r"(?P<rotations>\d+) (?P<rotation_type>\w+)$"),
        "shape": re.compile(r"^Shape (?P<id>\d+) \(Loops: (?P<loops>\d+), "
                            r"Quantity: (?P<quantity>\d+)\)$"),
        "loop": re.compile(r"^Loop (?P<id>\d+) \((?P<type>\w+)\): "
                           r"(?P<primitives>\d+) Primitives$"),
        "line": re.compile(r"^Line: (?P<begin>\(\d+\.\d+, \d+\.\d+\)),"
                           r"(?P<end>\(\d+\.\d+, \d+\.\d+\))$"),
        "arc_init": re.compile(r"^Arc: (?P<begin>\(\d+\.\d+, \d+\.\d+\)),"
                               r"(?P<end>\(\d+\.\d+, \d+\.\d+\)),$"),
        "arc_position": re.compile(r"^Cen: (?P<centre_point>\(\d+\.\d+, "
                                   r"\d+\.\d+\)), Rad: (?P<radius>\d+\.\d+),$"),
        "arc_angles": re.compile(r"^StAng: (?P<start_angle>[-]*\d+\.\d+), "
                                 r"Offset (?P<offset_angle>[-]*\d+\.\d+)$")
    }

    def __init__(self):
        super(StateMachine, self).__init__()

        self.current_state = self.STATES["profile"]
        self.file = ""
        self.sheetshape_size = [0.0, 0.0]
        self.sheetshape_rotation = 0.0

    def run(self):
        f = open(self.file, "r")

        self.begin()
        self.current_state = self.STATES["profile"]

        line_number = 0
        arc_data = None
        sh = None
        inner_loop = []

        shapes = []
        loop_type = ""
        lines = f.readlines()
        while self.current_state != self.STATES["end"]:
            line = lines[line_number].strip()

            if not line:
                line_number += 1
                if line_number >= len(lines):
                    self.current_state = self.STATES["end"]
                else:
                    continue

            if self.current_state == self.STATES["profile"]:
                match = self.EXPRESSIONS["profile"].search(line)
                if match:
                    self.profile(match.groupdict())
                    line_number += 1
                elif re.search(r"Shape \d+", line):
                    self.current_state = self.STATES["shape"]
                else:
                    self.current_state = self.STATES["end"]
            elif self.current_state == self.STATES["shape"]:
                match = self.EXPRESSIONS["shape"].search(line)
                if match:
                    sh = Shape()
                    self.shape(match.groupdict())
                    line_number += 1
                elif re.search(r"^Loop \d+", line):
                    self.current_state = self.STATES["loop"]
                else:
                    self.current_state = self.STATES["end"]
            elif self.current_state == self.STATES["loop"]:
                match = self.EXPRESSIONS["loop"].search(line)
                if match:
                    loop_data = match.groupdict()
                    loop_type = loop_data["type"]
                    self.loop(loop_data)
                    line_number += 1
                elif re.search(r"^Line:", line):
                    self.current_state = self.STATES["line"]
                elif re.search(r"^Arc:", line):
                    self.current_state = self.STATES["arc"]
                else:
                    self.current_state = self.STATES["end"]
            elif self.current_state == self.STATES["line"]:
                match = self.EXPRESSIONS["line"].search(line)
                if match:
                    if loop_type == "external":
                        sh.outer_loop.append(self.line(match.groupdict()))
                    elif loop_type == "internal":
                        inner_loop.append(self.line(match.groupdict()))
                    line_number += 1
                elif re.search(r"^Arc:", line):
                    self.current_state = self.STATES["arc"]
                elif re.search(r"^Loop \d+", line):
                    if inner_loop:
                        sh.inner_loops.append(inner_loop)
                    inner_loop = []

                    self.current_state = self.STATES["loop"]
                elif re.search(r"^Shape \d+", line):
                    if inner_loop:
                        sh.inner_loops.append(inner_loop)
                    inner_loop = []

                    shapes.append(sh)
                    sh = Shape()
                    self.current_state = self.STATES["shape"]
                elif re.search(r"^Profiles\d+:", line):
                    if inner_loop:
                        sh.inner_loops.append(inner_loop)
                    inner_loop = []

                    shapes.append(sh)
                    sh = Shape()
                    self.current_state = self.STATES["profile"]
                else:
                    if inner_loop:
                        sh.inner_loops.append(inner_loop)
                    inner_loop = []

                    self.current_state = self.STATES["end"]
            elif self.current_state == self.STATES["arc"]:
                match_init = self.EXPRESSIONS["arc_init"].search(line)
                match_position = self.EXPRESSIONS["arc_position"].search(line)
                match_angles = self.EXPRESSIONS["arc_angles"].search(line)
                if match_init:
                    arc_data = match_init.groupdict().items()
                    line_number += 1
                elif match_position:
                    arc_data = arc_data + match_position.groupdict().items()
                    line_number += 1
                elif match_angles:
                    arc_data = dict(arc_data + match_angles.groupdict().items())
                    if loop_type == "external":
                        sh.outer_loop.append(self.arc(arc_data))
                    elif loop_type == "internal":
                        inner_loop.append(self.arc(arc_data))
                    arc_data = None
                    line_number += 1
                elif re.search(r"^Line:", line):
                    self.current_state = self.STATES["line"]
                elif re.search(r"^Loop \d+", line):
                    if inner_loop:
                        sh.inner_loops.append(inner_loop)
                    inner_loop = []

                    self.current_state = self.STATES["loop"]
                elif re.search(r"^Shape \d+", line):
                    if inner_loop:
                        sh.inner_loops.append(inner_loop)
                    inner_loop = []

                    shapes.append(sh)
                    sh = Shape()
                    self.current_state = self.STATES["shape"]
                elif re.search(r"^Profiles\d+:", line):
                    if inner_loop:
                        sh.inner_loops.append(inner_loop)
                    inner_loop = []

                    shapes.append(sh)
                    sh = Shape()
                    self.current_state = self.STATES["profile"]
                else:
                    if inner_loop:
                        sh.inner_loops.append(inner_loop)
                    inner_loop = []

                    self.current_state = self.STATES["end"]
            elif self.current_state == self.STATES["end"]:
                shapes.append(sh)
                break

        self.end()
        print shapes

        for i in xrange(len(shapes)):
            shape = shapes[i]

            shape.position(0, 0)
            aabb = shape.bounds()
            size = (int(aabb.right - aabb.left) + 1,
                    int(aabb.top - aabb.bottom) + 1)
            r = Render()
            r.image_size = size
            r.shape(shape)
            r.save("reader{}.png".format(i))

        f.close()

    def begin(self):
        pass

    def profile(self, groups):
        size = ast.literal_eval(groups["size"])
        rotation = ast.literal_eval(groups["rotations"])

        self.sheetshape_size = size
        self.sheetshape_rotation = rotation

    def shape(self, groups):
        pass

    def loop(self, groups):
        pass

    def line(self, groups):
        line_shape = Line()

        begin = ast.literal_eval(groups["begin"])
        end = ast.literal_eval(groups["end"])

        line_shape.begin = Point(begin[0], begin[1])
        line_shape.end = Point(end[0], end[1])

        return line_shape

    def arc(self, groups):
        arc_shape = Arc()

        begin = ast.literal_eval(groups["begin"])
        end = ast.literal_eval(groups["end"])
        centre_point = ast.literal_eval(groups["centre_point"])
        radius = ast.literal_eval(groups["radius"])
        start_angle = ast.literal_eval(groups["start_angle"])
        offset_angle = ast.literal_eval(groups["offset_angle"])

        arc_shape.begin = Point(begin[0], begin[1])
        arc_shape.end = Point(end[0], end[1])
        arc_shape.centre_point = Point(centre_point[0], centre_point[1])
        arc_shape.radius = radius
        arc_shape.start_angle = start_angle
        arc_shape.offset_angle = offset_angle

        return arc_shape

    def end(self):
        pass

if __name__ == '__main__':
    if len(sys.argv) > 1:
        machine = StateMachine()
        machine.file = sys.argv[1]
        machine.run()
    else:
        print "Usage: {} <blf_data>".format(sys.argv[0])

