from models.molecule import *
from models.parser import *
from services.database import *

if __name__ == '__main__':
    parser = Parser()

    # extract molecule information
    molecule = Molecule(args='CHEBI:90')
    molecule.display()

    # clear all rows in tables
    database = Database()
    database.clear_tables()

    # save molecule
    database.save_molecule(molecule)
