#! python 2

import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import math


def CaptureAxialData(brep):
    d = 100
    x_axis_pos = rg.Line(rg.Point3d.Origin, rg.Point3d(d, 0, 0))
    x_axis_neg = rg.Line(rg.Point3d.Origin, rg.Point3d(-d, 0, 0))
    x1_data = GetAxialData(brep, x_axis_pos.ToNurbsCurve())
    x2_data = GetAxialData(brep, x_axis_neg.ToNurbsCurve())

    y_axis_pos = rg.Line(rg.Point3d.Origin, rg.Point3d(0, d, 0))
    y_axis_neg = rg.Line(rg.Point3d.Origin, rg.Point3d(0, -d, 0))
    y1_data = GetAxialData(brep, y_axis_pos.ToNurbsCurve())
    y2_data = GetAxialData(brep, y_axis_neg.ToNurbsCurve())

    z_axis_pos = rg.Line(rg.Point3d.Origin, rg.Point3d(0, 0, d))
    z_axis_neg = rg.Line(rg.Point3d.Origin, rg.Point3d(0, 0, -d))
    z1_data = GetAxialData(brep, z_axis_pos.ToNurbsCurve())
    z2_data = GetAxialData(brep, z_axis_neg.ToNurbsCurve())

    return [x1_data, x2_data, y1_data, y2_data, z1_data, z2_data] 

def GetAxialData(brep, half_axis_line):
    faces = brep.Faces
    point = None
    face = None

    # get face and point of intersection
    # has_more_faces = True
    # found_point = False
    # i = 0
    # total_faces = faces.Count
    # while (has_more_faces and not found_point):
    #     intersection = rg.Intersect.Intersection.CurveBrepFace(half_axis_line, faces[i], 0.001)
    #     p = intersection[2]
    #     c = intersection[1]
    #     if len(p) > 0:
    #         point = p[0]
    #         face = faces[i]
    #         found_point = True
    #     elif len(c) > 0:
    #         print('cab_bottom', 'i', i, 'faces', total_faces)
    #         point = c[0].PointAtStart
    #         found_point = True
    #         face = faces[i]
    #     else:
    #         i += 1
    #         if i == total_faces:
    #             has_more_faces = False
    #             print('reached end of faces')
        

    for f in faces:
        intersection = rg.Intersect.Intersection.CurveBrepFace(half_axis_line, f, 0.001)
        p = intersection[2]
        if len(p) > 0:
            point = p[0]
            face = f
            break

    # get u, v of point on face
    r, u, v = face.ClosestPoint(point)
    face_index = face.FaceIndex

    return [face_index, u, v]

def GetAxisLineFromData(brep, data1, data2):
    i1 = data1[0]
    u1 = data1[1]
    v1 = data1[2]

    i2 = data2[0]
    u2 = data2[1]
    v2 = data2[2]

    pnt1 = brep.Faces[i1].PointAt(u1, v1)
    pnt2 = brep.Faces[i2].PointAt(u2, v2)

    return (rg.Line(pnt1, pnt2))

def GetAxisLinesFromData(brep_id):
    brep = rs.coercebrep(brep_id)

    data1 = ReadAxialData(brep_id, 'x1_data')
    data2 = ReadAxialData(brep_id, 'x2_data')
    x_axis = GetAxisLineFromData(brep, data1, data2)

    data1 = ReadAxialData(brep_id, 'y1_data')
    data2 = ReadAxialData(brep_id, 'y2_data')
    y_axis = GetAxisLineFromData(brep, data1, data2)

    data1 = ReadAxialData(brep_id, 'z1_data')
    data2 = ReadAxialData(brep_id, 'z2_data')
    z_axis = GetAxisLineFromData(brep, data1, data2)

    return [x_axis, y_axis, z_axis]

def GetPlane(brep_id):
    x_axis, y_axis, z_axis = GetAxisLinesFromData(brep_id)
    t = rg.Intersect.Intersection.LineLine(x_axis, y_axis)[1]
    origin = x_axis.PointAt(t)

    # can't use this as it's rhino8-only
    # plane = rg.Plane.CreateFromNormalYup(origin, origin - z_axis.To, y_axis.From - y_axis.To)

    # work-around for lack of NormalYup function
    plane = rg.Plane(origin, z_axis.From - origin)
    vec1 = plane.YAxis
    vec2 = origin - y_axis.To
    angle = rg.Vector3d.VectorAngle(vec1, vec2, plane)
    if angle >= 0:
        plane.Rotate(angle, plane.ZAxis)
    
    return plane

def GetSizeData(brep_id):
    x_axis, y_axis, z_axis = GetAxisLinesFromData(brep_id)
    width = x_axis.Length
    length = y_axis.Length
    depth = z_axis.Length
    return [width, length, depth]

# reads the axial data and returns a face index and the u,v of a point on the face
# these data can be used to make the from and to points of each axis
def ReadAxialData(brep_id, key):
    data = rs.GetUserText(brep_id, key)
    data = data.replace('[', '')
    data = data.replace(']', '')
    data = data.replace(' ', '')
    data = data.split(',')

    data[0] = int(data[0])
    data[1] = float(data[1])
    data[2] = float(data[2])

    return data

# reads the size data and returns the width, length, and depth
def ReadScaleData(brep_id):
    data = rs.GetUserText(brep_id, 'scale_data')
    data = data.replace('[', '')
    data = data.replace(']', '')
    data = data.replace(' ', '')
    data = data.split(',')

    for i in range(len(data)):
        data[i] = float(data[i])

    return data

def WriteAxialData(brep_id, axial_data):
    rs.SetUserText(brep_id, 'x1_data', axial_data[0])
    rs.SetUserText(brep_id, 'x2_data', axial_data[1])
    rs.SetUserText(brep_id, 'y1_data', axial_data[2])
    rs.SetUserText(brep_id, 'y2_data', axial_data[3])
    rs.SetUserText(brep_id, 'z1_data', axial_data[4])
    rs.SetUserText(brep_id, 'z2_data', axial_data[5])

def WriteSpatialData(brep_id, axial_data, scale_data):
    WriteAxialData(brep_id, axial_data)
    WriteScaleData(brep_id, scale_data)

def WriteScaleData(brep_id, scale_data):
    rs.SetUserText(brep_id, 'scale_data', scale_data)
















