import ctypes

class Position(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]

class Velocity(ctypes.Structure):
    _fields_ = [("vx", ctypes.c_float), ("vy", ctypes.c_float)]

class Entity(ctypes.Structure):
    _fields_ = [("position", Position), ("velocity", Velocity)]

class Boids(ctypes.Structure):
    pass
Boids._fields_ = [("entities", ctypes.POINTER(Entity)), ("count", ctypes.c_int)]

class BoidNode(ctypes.Structure):
    pass
BoidNode._fields_ = [
    ("boid_entity", ctypes.POINTER(Entity)),
    ("next", ctypes.POINTER(BoidNode)),
]

class Grid(ctypes.Structure):
    _fields_ = [
        ("rows", ctypes.c_int),
        ("cols", ctypes.c_int),
        ("cell_size", ctypes.c_float),
        ("cells", ctypes.POINTER(ctypes.POINTER(BoidNode))),
    ]