from models.molecule import *
from services.database import *
import json


class Parser:

    def __init__(self):
        # initialize molecules SDF file path from JSON config file
        config_file = open('config.json')
        configuration = json.load(config_file)
        self.source_path = configuration['chebi']['path']

    # open & read SDF file from local storage file 'chEBI_complete_3star.sdf'
    def read_sdf_file(self):
        with open(self.source_path, 'r') as f:
            source = f.readlines()  # get from SDF all molecules information
            f.close()
        return source

    # read & extract all chEBI molecules IDs
    def extract_molecules_ID(self):
        # read SDF file & extract all information inside buffer 'data'
        molecules_id = []
        data = self.read_sdf_file()
        index = 0

        # extract all molecules ID from buffer 'data'
        for line in data:
            if index == 1:
                molecules_id.append(line.strip())
                index = 0
                continue
            if "<ID>" in line or "<ChEBI ID>" in line:
                index = 1
                continue
        return molecules_id

    # principal function of parsing
    def run(self):

        # extract molecules IDs
        molecules_id = self.extract_molecules_ID()

        # extract information of each ChEBI ID
        counter = 0
        database_service = Database()

        for id_chebi in molecules_id:

            # display parsing state
            counter += 1
            print(f'Molecule N°{counter}')

            # extract information & parse molecular structure
            molecule = Molecule(args=id_chebi)

            # save molecule in SQL database
            database_service.save_molecule(molecule)
