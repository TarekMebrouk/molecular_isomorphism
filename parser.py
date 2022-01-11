import numpy as np
import queue
from bioservices import ChEBI


class Parser:

    def __init__(self):
        # initialize molecules file path
        self.source_path = 'ChEBI_complete_3star.sdf'

        # initialize molecules IDs
        self.molecules_ID = []
        self.debug_level = 0

        # initialize bio service library
        self.service_library = ChEBI()

    # open & read SDF file from local storage file 'chEBI_complete_3star.sdf'
    def read_sdf_file(self):
        with open(self.source_path, 'r') as f:
            source = f.readlines()  # get from SDF all molecules information
            f.close()
        return source

    # read & extract all chEBI molecules IDs
    def extract_molecules_ID(self):
        # read SDF file & extract all information inside buffer 'data'
        data = self.read_sdf_file()
        index = 0

        # extract all molecules ID from buffer 'data'
        for line in data:
            if index == 1:
                self.molecules_ID.append(line.strip())
                index = 0
                continue
            if "<ID>" in line or "<ChEBI ID>" in line:
                index = 1
                continue
        if self.debug_level >= 5:
            print(self.molecules_ID)

    # get & extract all molecule information from ID
    def get_molecule(self, molecule_id):

        # get complete entity of molecule by here ID
        molecule_entity = self.service_library.getCompleteEntity(molecule_id)

        # get molecule 'name'
        molecule_name = molecule_entity.chebiAsciiName

        # get molecule 'formula'
        molecule_formula = molecule_entity.Formulae[0]['data']

        # get molecule 'dimension'
        molecule_dimension = molecule_entity.ChemicalStructures[0]['dimension']

        # get molecule 'type' : composed or not
        molecule_composed = '.' in molecule_formula

        # get molecule 'atoms_id' & 'links'
        molecule_atoms_id, molecule_links = [], []
        if not molecule_composed:
            molecule_atoms_id, molecule_links = self.get_structure(molecule_entity)

        # delete all 'H' atoms from atoms & links lists
        if not molecule_composed:
            molecule_atoms_id, molecule_links = self.delete_H_from_molecule(molecule_atoms_id, molecule_links)

        # get molecule 'atoms' used
        molecule_atoms = []
        if not molecule_composed:
            for atom in molecule_atoms_id:
                molecule_atoms.append(atom[0])
        molecule_atoms = list(dict.fromkeys(molecule_atoms))  # delete duplicates atoms from list

        # get maximum type of link between atoms
        molecule_maximum_link = self.get_max_link_type(molecule_links)

        # get molecule 'family'
        molecule_family = None
        if not molecule_composed:
            molecule_family = self.get_family(molecule_atoms, molecule_atoms_id, molecule_links)

        # sorting atoms list
        molecule_atoms_id.sort()
        molecule_atoms.sort()

        # transform link before launching isomorphism algorithm
        molecule_atoms_transformed, molecule_links_transformed = self.transform_links(molecule_atoms_id, molecule_links)

        # get PTN & LAB array of molecule
        molecule_lab, molecule_ptn = self.construct_lab_ptn(molecule_atoms_transformed)

        # create molecule dictionary
        return {
            'ID': molecule_id,
            'NAME': molecule_name,
            'FORMULA': molecule_formula,
            'DIMENSIONS': molecule_dimension,
            'COMPOSED': molecule_composed,
            'ATOMS': molecule_atoms,
            'ATOMS_NUMBER': len(molecule_atoms_id),
            'LINKS_NUMBER': len(molecule_links),
            'ATOMS_ID': molecule_atoms_id,
            'LINKS': molecule_links,
            'FAMILY': molecule_family,
            'MAXIMUM_LINK': molecule_maximum_link,
            'ATOMS_NUMBER_TRANSFORMED': len(molecule_atoms_transformed),
            'LINKS_NUMBER_TRANSFORMED': len(molecule_links_transformed),
            'ATOMS_TRANSFORMED': molecule_atoms_transformed,
            'LINKS_TRANSFORMED': molecule_links_transformed,
            'LAB': molecule_lab,
            'PTN': molecule_ptn
        }

    # parse structure & get molecule atoms and links
    @staticmethod
    def get_structure(molecule_entity):

        # get molecule structure (transition matrix between atoms)
        buffer = molecule_entity.ChemicalStructures[0]['structure'].splitlines()
        molecule_structure = []
        for i in buffer:
            molecule_structure.append(i.split())

        # get encoding type of molecule (by default 'marven')
        molecule_encoding_type = molecule_structure[1][0]

        # check if encoding type of molecule equals to 'Marvin'
        encoder_list = {'Marvin': (16, 7)}
        if molecule_encoding_type not in encoder_list:
            print('Error:: missing Marven inside molecule encoding type')
            return None

        # get dimensions of atoms & links list
        dim_atoms = encoder_list[molecule_encoding_type][0]
        dim_links = encoder_list[molecule_encoding_type][1]

        # extract atoms & links from molecule structure 'Marven'
        a_ch, l_ch, atom_id = 0, 0, 0
        atoms, links = [], []

        for line in molecule_structure:
            if len(line) == dim_atoms and l_ch == 0:
                a_ch = 1
                atoms.append((line[3], atom_id))  # add new atom
                atom_id += 1
                continue

            if len(line) == dim_links and a_ch == 1:
                l_ch = 1
                links.append((int(line[0]) - 1, int(line[1]) - 1, line[2]))  # add new link
                continue

            if len(line) != dim_links and l_ch == 1:
                break

        return atoms, links

    # get maximum link type inside molecules links (detect multiple & triple links)
    @staticmethod
    def get_max_link_type(molecule_links):
        return max([int(link_type) for _, _, link_type in molecule_links])

    # delete all 'H' atoms from molecule (to speed up isomorphism detection algorithm)
    @staticmethod
    def delete_H_from_molecule(molecule_atoms_id, molecule_links):
        delete_atoms = []
        delete_links = []

        for i in range(0, len(molecule_atoms_id)):
            atom_name, atom_id = molecule_atoms_id[i]
            if atom_name == 'H':
                for j in range(0, len(molecule_links)):
                    atom_form, atom_to, link_type = molecule_links[j]
                    if atom_to == atom_id or atom_form == atom_id:
                        delete_links.append(j)
                delete_atoms.append(i)

        # delete atoms
        for x in delete_atoms:
            molecule_atoms_id = molecule_atoms_id[:x] + molecule_atoms_id[x+1:]

        # delete links
        for y in delete_links:
            molecule_links = molecule_links[:y] + molecule_links[y+1:]

        return molecule_atoms_id, molecule_links

    # get & classify molecule family
    @staticmethod
    def get_family(molecule_atoms, molecule_atoms_id, molecule_links):
        # initialize family classification sorted by there orderIDs
        families = {
            0: 'Amide',
            1: 'Amine',
            2: 'Ester',
            3: 'Carboxylic acid',
            4: 'Ketone',
            5: 'Aldehyde',
            6: 'Alcohol',
            7: 'Halogenated compound',
            8: 'Aromatic compound',
            9: 'Alken',
            10: 'Alkanes',
            11: 'Other'
        }
        classification = [False] * len(families)

        # initialize atoms links dictionary
        links_dictionary = Parser.get_links_dictionary(molecule_atoms_id, molecule_links)

        # get characteristics of molecules structure
        # 1 - check if molecule family = 'Halogenated compound'
        # check if atoms list contains one of these atoms ['F', 'Cl', 'Br', 'I' ]
        classification[7] = any(element for element in [atom in molecule_atoms for atom in ['F', 'Cl', 'Br', 'I']])

        # 2 - check if molecule family = 'Alkanes' or 'Alken'
        # check if atoms list contains only ['C', 'H']
        classification[10] = all(element for element in [atom in ['C', 'H'] for atom in molecule_atoms])
        # check if atoms list contains 'C' with multiple links
        if classification[10]:
            for link in molecule_links:
                if link[2] == '2':
                    classification[9] = True
                    break

        # 3 - check if molecule family = 'Alcohol'
        # check if atoms list contains [Atom : 'O']
        if any(atom == 'O' for atom in molecule_atoms):

            # check if links list contains at least [link : R-O-H ] for each atom 'O'
            for atom in molecule_atoms_id:
                atom_name, atom_id = atom
                if atom_name == 'O':
                    # get links of the current atom from links dictionary
                    if len(links_dictionary[atom_id]) == 1:
                        # check link type (must be type = '1')
                        _, _, link_type = links_dictionary[atom_id][0]
                        if link_type == 1:
                            classification[6] = True
                            break

                # check if R-O-H already found
                if classification[6]:
                    break

        # 4 - check if molecule family = 'Amine'
        # check if atoms list contains [Atom : 'N']
        if any(atom == 'N' for atom in molecule_atoms):
            # check if links list contains at least [link : R1-N, R2-N, R3-N] for each atom 'N'
            for atom in molecule_atoms_id:
                atom_name, atom_id = atom
                if atom_name == 'N':
                    # get links of the current atom from links dictionary
                    # check if atom related with 3 other atoms
                    if len(links_dictionary[atom_id]) == 3:
                        classification[1] = True
                        break

        # 5 - check if molecule family = 'Amide', 'Ester', 'Carboxylic acid', 'Ketone', 'Aldehyde'
        # check all atoms 'C' with link 'C'='O'
        for atom_id in links_dictionary.keys():
            atom_name, _ = [atom for atom in molecule_atoms_id if atom[1] == atom_id][0]

            # check if current atom is 'C'
            if atom_name == 'C':

                for link in links_dictionary[atom_id]:
                    linked_atom_id, linked_atom_name, link_type = link

                    # check if current atom is linked with 'C'='O'
                    if linked_atom_name == 'O' and link_type == 2:

                        # check the type of atom who is linked in
                        # check if R-C , family = 'Aldehyde'
                        if len(links_dictionary[atom_id]) == 2:
                            classification[5] = True
                        else:
                            # check if R-C-N , family = 'Amide'
                            if any(element for element in [link[1] == 'N' for link in links_dictionary[atom_id]]):
                                classification[0] = True
                            # check if R-C-OH , family = 'Carboxylic acid'
                            if any(element for element in [link[1] == 'O' and link[2] == 1 for link in links_dictionary[atom_id]]):
                                classification[3] = True

                                # check if R-C-O-R , family = 'Ester'
                                temp = [link[0] for link in links_dictionary[atom_id] if link[1] == 'O' and link[2] == 1]
                                if any(len(links_dictionary[atom_linked]) > 1 for atom_linked in temp):
                                    classification[2] = True
                            # check if C-C-C , Family = 'Ketone'
                            if len([link for link in links_dictionary[atom_id] if link[1] == 'C']) == 2:
                                classification[4] = True

        # 5 - check if molecule family = 'aromatic compound'
        # check if exists cycle inside molecular graph
        if Parser.isContains_cycle(molecule_atoms_id, molecule_links):
            classification[8] = True

        # return family after classification by order
        for i in range(len(classification)):
            if classification[i]:
                return families[i]

        # if any family is selected return 'Other'
        return families[-1]

    # create molecule dictionary {'atom_id' : ['neighbor1_id', 'neighbor2_id', ...], ... }
    @staticmethod
    def get_links_dictionary(molecule_atoms_id, molecule_links):
        links_dictionary = {}

        # sort atoms_id by there ID
        molecule_atoms_id.sort(key=lambda element: element[1])

        # complete the dictionary for each molecule with all its links
        for atom in molecule_atoms_id:
            atom_name, atom_id = atom
            links_dictionary[atom_id] = []

            for link in molecule_links:
                atom_from, atom_to, link_type = link

                # check if the atom 'atom_id' is part of the current 'link'
                if atom_to == atom_id or atom_from == atom_id:

                    # get linked atom id
                    if atom_from == atom_id:
                        linked_atom_id = atom_to
                    else:
                        linked_atom_id = atom_from

                    # get linked atom name from atoms_id list
                    linked_atom_name, _ = [atom for atom in molecule_atoms_id if atom[1] == linked_atom_id][0]

                    # append linked atom inside dictionary
                    links_dictionary[atom_id].append((linked_atom_id, linked_atom_name, int(link_type)))

        return links_dictionary

    # detect if molecule graph contains cycle (detect aromatic cycles for family classification)
    @staticmethod
    def isContains_cycle(molecule_atoms_id, molecule_links):
        # construct dictionary for each atom with its neighbors
        links_dictionary = {}
        for atom in molecule_atoms_id:
            _, atom_id = atom
            links_dictionary[atom_id] = []
            for link in molecule_links:
                from_id, to_id, _ = link
                if atom_id == from_id:
                    links_dictionary[atom_id].append(to_id)
                if atom_id == to_id:
                    links_dictionary[atom_id].append(from_id)

        # make in-depth course (DFS) for constructing graph & detecting cycles
        visited_nodes = []
        current_nodes = queue.Queue()
        current_nodes.put(molecule_atoms_id[0][1])

        while not current_nodes.empty():
            node = current_nodes.get()
            # get all neighbors of selected node
            for neighbor in links_dictionary[node]:
                # check if neighbor is already inside current nodes (cycle detected)
                if neighbor in np.array(current_nodes.queue):
                    return True

                # put the neighbor inside current nodes
                else:
                    links_dictionary[neighbor].remove(node)
                    current_nodes.put(neighbor)

            # put the selected node to visited nodes
            # check if node already exists in visited nodes (cycle detected)
            if node in visited_nodes:
                return True
            else:
                visited_nodes.append(node)
        return False

    # link coloring step : transform links (replace 2-link & 3-link with new atoms 'XXX')
    @staticmethod
    def transform_links(molecule_atoms_id, molecule_links):

        # create new temporary atoms & links lists
        temp_atoms = [(atom_name, atom_id, '0') for atom_name, atom_id in molecule_atoms_id]
        temp_links = [(link_from, link_to, '0') for link_from, link_to, _ in molecule_links]

        # link coloring for 2-link & 3-link
        atom_id = len(molecule_atoms_id)
        for link in molecule_links:
            link_from, link_to, link_type = link

            # if link = double link 'link-2'
            if link_type == '2':
                # add one new atom 'XXX'
                temp_atoms.append(('XXX', atom_id, '1'))
                # add link from-XXX-to
                temp_links.append((link_from, atom_id, '1'))
                temp_links.append((link_to, atom_id, '1'))
                atom_id += 1

            # if link = triple link 'link-3'
            if link_type == '3':
                # add first new atoms 'XXX' with its links
                temp_atoms.append(('XXX', atom_id, '1'))
                temp_links.append((link_from, atom_id, '1'))
                temp_links.append((link_to, atom_id, '1'))
                atom_id += 1

                # add second new atom 'XXX' with its links
                temp_atoms.append(('XXX', atom_id, '1'))
                temp_links.append((link_from, atom_id, '1'))
                temp_links.append((link_to, atom_id, '1'))
                atom_id += 1

        return temp_atoms, temp_links

    # construct LAB & PTN arrays for isomorphism algorithm ('Nauty MCKAY')
    @staticmethod
    def construct_lab_ptn(molecule_atoms):
        # sorting molecule atoms list & initialize temporary lists
        molecule_atoms.sort()
        ptn = []

        # construct Lab & lab_mol arrays
        lab = [atom_id for _, atom_id, _ in molecule_atoms]
        lab_mol = [atom_name for atom_name, _, _ in molecule_atoms]

        # construct PTN array
        i = 1
        while i < len(lab_mol):
            if lab_mol[i - 1] == lab_mol[i]:
                ptn.append(1)
            else:
                ptn.append(0)
            i += 1
        ptn.append(0)

        # transform LAB array to string & separate atoms IDs with '-'
        temp = [str(elem) for elem in lab]
        converted_lab = '-'.join(temp)

        # transform PTN array to string
        temp = [str(elem) for elem in ptn]
        converted_ptn = ''.join(temp)

        return converted_lab, converted_ptn

    @staticmethod
    def display_molecule(molecule_dictionary):
        print('---------------------------------------------------------------------')
        print('ID : ', molecule_dictionary['ID'])
        print('NAME : ', molecule_dictionary['NAME'])
        print('FORMULA : ', molecule_dictionary['FORMULA'])
        print('DIMENSIONS : ', molecule_dictionary['DIMENSIONS'])
        print('COMPOSED : ', molecule_dictionary['COMPOSED'])
        print('FAMILY : ', molecule_dictionary['FAMILY'])
        print('ATOMS NUMBER : ', molecule_dictionary['ATOMS_NUMBER'])
        print('LINKS NUMBER : ', molecule_dictionary['LINKS_NUMBER'])
        print('ATOMS : ', molecule_dictionary['ATOMS'])
        print('ATOMS_ID : ', molecule_dictionary['ATOMS_ID'])
        print('LINKS : ', molecule_dictionary['LINKS'])
        print('MAXIMUM_LINK_TYPE : ', molecule_dictionary['MAXIMUM_LINK'])
        print('ATOMS_NUMBER_TRANSFORMED : ', molecule_dictionary['ATOMS_NUMBER_TRANSFORMED'])
        print('LINKS_NUMBER_TRANSFORMED : ', molecule_dictionary['LINKS_NUMBER_TRANSFORMED'])
        print('ATOMS_TRANSFORMED : ', molecule_dictionary['ATOMS_TRANSFORMED'])
        print('LINKS_TRANSFORMED : ', molecule_dictionary['LINKS_TRANSFORMED'])
        print('LAB : ', molecule_dictionary['LAB'])
        print('PTN : ', molecule_dictionary['PTN'])
        print('---------------------------------------------------------------------')


if __name__ == '__main__':
    parser = Parser()
    molecule = parser.get_molecule('CHEBI:90')
    parser.display_molecule(molecule)
