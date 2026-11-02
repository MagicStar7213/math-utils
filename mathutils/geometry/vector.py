from sympy import Mul, acos
from mathutils.matrices.utils import Matrix

class Vector(Matrix):
    """Representation of a vector without reference system. It can be 2D or 3D
    Parameters:
    - x: X coordinate
    - y: Y coordinate
    - z (optional): Z coordinate"""

    def __new__(cls, *coords):
        return super().__new__(cls, 1, len(coords), list(coords))

    def _pretty(self, printer):
        return printer._print_MatrixBase(self, lparens='(', rparens=')')

    @property
    def components(self):
        """Returns the vector's coordinates as a tuple"""
        return tuple(self.flat())

    def __mul__(self, other: 'Vector'):
        return self.dot(other)

    def __xor__(self, other: 'Vector'):
        return self.cross(other)

    def __str__(self) -> str:
        return str(self.components)

    def angle_between(self, v: 'Vector'):
        """Returns the angle between the vector and another one, v"""
        return acos((self.dot(v))/Mul(self.norm(),v.norm()))
