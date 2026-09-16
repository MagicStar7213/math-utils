from sympy import Matrix, Mul, acos, sqrt, symbols

class Vector():
    """Representation of a vector without reference system. It can be 2D or 3D
    Parameters:
    - x: X coordinate
    - y: Y coordinate
    - z (optional): Z coordinate"""
    def __init__(self, x, y, z=None) -> None:
        self.x = x
        self.y = y
        self.z = z if z is not None else 0
        self.components = (self.x,self.y) + (tuple([z]) if z is not None else tuple())

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __add__(self, other: 'Vector'):
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self, other: 'Vector'):
        return self + (-other)

    def __mul__(self, other: 'Vector'):
        return self.escalar(other)

    def __rmul__(self, other):
        return Vector(other*self.x, other*self.y, other*self.z)

    def __xor__(self, other: 'Vector'):
        return self.vectorial(other)

    def __str__(self) -> str:
        return str(self.components)

    def length(self):
        """Returns the magnitude or length of the vector"""
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def angle_between(self, v):
        """Returns the angle between the vector and another one, v"""
        return acos((self*v)/Mul(self.length(),v.length()))

    def escalar(self, v: 'Vector'):
        """Returns the dot product of the vector with another, v"""
        return self.x*v.x + self.y*v.y + self.z*v.z

    def vectorial(self, v:'Vector'):
        """Returns the cross product of the vector times another, v"""
        i,j,k = symbols('i j k')
        vec = Matrix([[i,j,k],[self.x,self.y,self.z],[v.x,v.y,v.z]]).det()
        return Vector(vec.coeff(i), vec.coeff(j), vec.coeff(k))

    def mixto(self, v:'Vector', w: 'Vector'):
        """Returns the mixed product of 3 vectors: self, v and w"""
        return self.escalar(v.vectorial(w))
