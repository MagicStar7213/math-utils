from sympy import init_printing
from .matrices.main import matrices
from .geometry.main import main as geometry

init_printing()
print("""
  __  __       _   _       _   _ _   _ _     
 |  \\/  | __ _| |_| |__   | | | | |_(_) |___ 
 | |\\/| |/ _` | __| '_ \\  | | | | __| | / __|
 | |  | | (_| | |_| | | | | |_| | |_| | \\__ \\
 |_|  |_|\\__,_|\\__|_| |_|  \\___/ \\__|_|_|___/
                                             
""")
option = input('Elige un campo. Geometría [g], Álgebra [a] o Salir [q]: ').strip()
while option != "q":
    if option == "g":
        geometry()
    elif option == "a":
        matrices()
