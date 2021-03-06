# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""


import qt.QtCore as qc
import qt.QtGui as qg

import sympy
import sympy.utilities
import popupcad
from popupcad.constraints.constraint_system import ConstraintSystem
from popupcad.constraints.constraint import Constraint,ValueConstraint
from popupcad.constraints.constraint_support import *     

class FixedConstraint(Constraint):
    name = 'Fixed'
    validity_tests = [Constraint.at_least_one_point]
    
    def __init__(self, vertex_ids, values):
        self.vertex_ids = vertex_ids
        self.segment_ids = []
        self.values = values
        self.id = id(self)

    @classmethod
    def new(cls, *objects):
        from popupcad.geometry.line import Line
        from popupcad.geometry.vertex import BaseVertex

        segment_ids = [tuple(sorted((line.vertex1.id, line.vertex2.id))) for line in objects if isinstance(line, Line)]
        segment_ids = list(set(segment_ids))

        vertex_ids = []
        vertex_ids.extend([(vertex.id, vertex.getpos()) for vertex in objects if isinstance(vertex, BaseVertex)])
        vertex_ids.extend([(vertex.id, vertex.getpos()) for line in objects if isinstance(line,Line) for vertex in (line.vertex1,line.vertex2)])
        vertex_ids = dict(vertex_ids)

        obj = cls(list(vertex_ids.keys()), list(vertex_ids.values()))
        obj.check_valid()
        return obj

    def copy(self, identical=True):
        new = type(self)(self.vertex_ids, self.values)
        if identical:
            new.id = self.id
        return new

    def symbolic_equations(self):
        eqs = []
        for vertex, val in zip(self.getvertices(), self.values):
            eqs.append(vertex.p()[0] - val[0])
            eqs.append(vertex.p()[1] - val[1])
        return eqs


class HorizontalConstraint(Constraint):
    name = 'Horizontal'
    validity_tests = [Constraint.at_least_two_points]

    def symbolic_equations(self):
        vertices = self.getallvertices()
        eqs = []
        vertex0 = vertices.pop(0)
        p0 = vertex0.p()
        for vertex in vertices:
            eqs.append(vertex.p()[1] - p0[1])
        return eqs


class VerticalConstraint(Constraint):
    name = 'Vertical'
    validity_tests = [Constraint.at_least_two_points]

    def symbolic_equations(self):
        vertices = self.getallvertices()
        eqs = []
        vertex0 = vertices.pop(0)
        p0 = vertex0.p()
        for vertex in vertices:
            eqs.append(vertex.p()[0] - p0[0])
        return eqs


class DistanceConstraint(ValueConstraint):
    name = 'distance'
    validity_tests = [Constraint.exactly_two_points]

    def symbolic_equations(self):
        vertices = self.getallvertices()
        p0 = vertices[0].p()
        p1 = vertices[1].p()
        if self.value == 0.:
            eq = []
            eq.append(p1[0] - p0[0])
            eq.append(p1[1] - p0[1])
            return eq
        else:
            v1 = p1 - p0
            l1 = v1.dot(v1)**.5
            eq = l1 - self.value
            return [eq]


class CoincidentConstraint(Constraint):
    name = 'Coincident Points'
    validity_tests = [Constraint.at_least_two_points]

    def symbolic_equations(self):
        vertices = self.getallvertices()
        eq = []
        p0 = vertices.pop().p()
        for vertex in vertices:
            p = vertex.p()
            eq.append(p[0] - p0[0])
            eq.append(p[1] - p0[1])
        return eq


class XDistanceConstraint(ValueConstraint):
    name = 'X Distance'
    validity_tests = [Constraint.at_least_one_point]

    def symbolic_equations(self):
        vertices = self.getallvertices()
        if len(vertices) == 1:
            eq = vertices[0].p()[0] - self.value
        else:
            eq = ((vertices[1].p()[0] - vertices[0].p()[0])**2)**.5 - \
                ((self.value)**2)**.5
        return [eq]


class YDistanceConstraint(ValueConstraint):
    name = 'Y Distance'
    validity_tests = [Constraint.at_least_one_point]

    def symbolic_equations(self):
        vertices = self.getallvertices()
        if popupcad.flip_y:
            temp = 1.
        else:
            temp = -1.
        if len(vertices) == 1:
            eq = vertices[0].p()[1] - self.value * temp
        else:
            eq = ((vertices[1].p()[1] - vertices[0].p()[1])**2)**.5 - \
                ((self.value)**2)**.5
        return [eq]


class AngleConstraint(ValueConstraint):
    name = 'Angle'
    value_text = 'enter angle(in degrees)'
    validity_tests = [Constraint.at_least_one_line]

    def symbolic_equations(self):
        lines = self.getlines()[0:2]

        if len(lines) == 1:
            v1 = lines[0].v()
            v2 = sympy.Matrix([1, 0, 0])
            l2 = 1
        elif len(lines) == 2:
            v1 = lines[0].v()
            v2 = lines[1].v()
            l2 = v2.dot(v2)**(.5)
        if self.value != 0:
            l1 = v1.dot(v1)**(.5)
            v3 = v1.cross(v2)
            l3 = v3.dot(v3)**.5
            eq = l3 - sympy.sin(self.value * sympy.pi / 180) * l1 * l2
        else:
            if len(lines) == 1:
                eq = v1[1]
            elif len(lines) == 2:
                eq = v2[0] * v1[1] - v2[1] * v1[0]
        return [eq]


class ParallelLinesConstraint(Constraint):
    name = 'Parallel Lines'
    validity_tests = [Constraint.at_least_two_lines]

    def symbolic_equations(self):
        lines = self.getlines()
        v1 = lines.pop(0).v()
        eq = []
        for line in lines:
            v2 = line.v()
            eq.append(v2[0] * v1[1] - v2[1] * v1[0])
        return eq


class EqualLengthLinesConstraint(Constraint):
    name = 'Equal Length Lines'
    validity_tests = [Constraint.at_least_two_lines]

    def symbolic_equations(self):
        lines = self.getlines()
        vs = [line.v() for line in lines]
        lengths = [v.dot(v)**.5 for v in vs]
        eqs = []
        length0 = lengths.pop(0)
        for length in lengths:
            eqs.append(length0 - length)
        return eqs


class PerpendicularLinesConstraint(Constraint):
    name = 'Perpendicular Lines'
    validity_tests = [Constraint.exactly_two_lines]

    def symbolic_equations(self):
        lines = self.getlines()[0:2]
        v1 = lines[0].v()
        v2 = lines[1].v()
        return [v2[1] * v1[1] + v2[0] * v1[0]]


class PointLineDistanceConstraint(ValueConstraint):
    name = 'Point-Line Distance'
    validity_tests = [Constraint.exactly_one_point_and_one_line]

    def symbolic_equations(self):
        line = self.getlines()[0]
        p1 = self.getvertices()[0].p()
        v1 = p1 - line.p1()
        v = line.v()
        lv = line.lv()
        a = v.dot(v1) / lv
        p0 = v * a / lv + line.p1()

        if self.value == 0.:
            eq = []
            eq.append(p1[0] - p0[0])
            eq.append(p1[1] - p0[1])
            return eq
        else:
            v1 = p1 - p0
            l1 = v1.dot(v1)**.5
            eq = l1 - self.value
            return [eq]


class LineMidpointConstraint(Constraint):
    name = 'Point on Line Midpoint'
    validity_tests = [Constraint.exactly_one_point_and_one_line]

    def symbolic_equations(self):
        line = self.getlines()[0]
        p1 = self.getvertices()[0].p()
        p0 = (line.p1() + line.p2()) / 2

        eq = []
        eq.append(p1[0] - p0[0])
        eq.append(p1[1] - p0[1])
        return eq

if __name__ == '__main__':
#    a = SymbolicVertex(1)
#    b = SymbolicVertex(2)
#    c = SymbolicVertex(3)
#    d = SymbolicVertex(4)
    
#    line1 = a,b
#    line2 = b,c

    constraint = perpendicular([],[(1,2),(3,4)])