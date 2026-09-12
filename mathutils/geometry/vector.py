from sympy import Matrix, Mul, acos, sqrt, symbols

class Vector():
    def __init__(self, x, y, z) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.components = (x,y,z)
    
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
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def angle_between(self, v):
        return acos((self*v)/Mul(self.length(),v.length()))

    def escalar(self, v: 'Vector'):
        return self.x*v.x + self.y*v.y + self.z*v.z
    
    def vectorial(self, v:'Vector'):
        i,j,k = symbols('i j k')
        vec = Matrix([[i,j,k],[self.x,self.y,self.z],[v.x,v.y,v.z]]).det()
        return Vector(vec.coeff(i), vec.coeff(j), vec.coeff(k))
    
    def mixto(self, v:'Vector', w: 'Vector'):
        return self.escalar(v.vectorial(w))