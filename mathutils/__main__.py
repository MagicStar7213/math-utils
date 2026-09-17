from sympy import init_printing
from .matrices.main import matrices
from .geometry.main import main as geometry

def main():
    init_printing()
    print("""
  __  __       _   _       _   _ _   _ _     
 |  \\/  | __ _| |_| |__   | | | | |_(_) |___ 
 | |\\/| |/ _` | __| '_ \\  | | | | __| | / __|
 | |  | | (_| | |_| | | | | |_| | |_| | \\__ \
 |_|  |_|\\__,_|\\__|_| |_|  \\___/ \\__|_|_|___/
                                             
""")
    while True:
        option = input('Elige un campo. Geometría [g], Matrices [m] o Salir [q]: ')
        if option == "g":
            geometry()
        elif option == "m":
            matrices()
        elif option == "q":
            exit(0)

main()