import numpy as np
import queue
from bioservices import ChEBI


class Molecule:

    # initialize bio service library
    service_library = ChEBI()

    def __init__(self, id):
        # initialize molecule id
        self.id = id

        # get complete entity of molecule by here ID from bio-service library
        self.molecule_entity = self.service_library.getCompleteEntity(id)

        # get molecule 'name'
        self.name = self.molecule_entity.chebiAsciiName

        # get molecule 'formula'
        self.formula = self.molecule_entity.Formulae[0]['data']

        # get molecule 'dimension'
        self.dimension = self.molecule_entity.ChemicalStructures[0]['dimension']

        # get molecule 'type' : composed or not
        self.composed = '.' in self.formula

        # get molecule 'atoms_id' & 'links'
        self.atoms_id, self.links = [], []
        if not self.composed:
            self.atoms_id, self.links = self.get_structure()

        # delete all 'H' atoms from atoms & links lists
        if not self.composed:
            self.atoms_id, self.links = self.delete_H_from_molecule()

        # init number of atoms & links
        self.atoms_number = len(self.atoms_id)
        self.links_number = len(self.links)

        # get molecule 'atoms' used
        self.atoms = []
        if not self.atoms:
            for atom in self.atoms_id:
                self.atoms.append(atom[0])
        self.atoms = list(dict.fromkeys(self.atoms))  # delete duplicates atoms from list

        # get maximum type of link between atoms
        self.maximum_link = self.get_max_link_type()

        # get molecule 'family'
        self.family = None
        if not self.composed:
            self.family = self.get_family()

        # sorting atoms list
        self.atoms_id.sort()
        self.atoms.sort()

        # transform link before launching isomorphism algorithm
        self.atoms_colored, self.links_colored = self.transform_links_colored()

        # init number of atoms & links
        self.atoms_colored_number = len(self.atoms_colored)
        self.links_colored_number = len(self.links_colored)

        # get PTN & LAB array of molecule
        self.lab = self.construct_lab()
        self.ptn_atoms_colored = self.construct_ptn_atoms_colored()
        self.ptn_links_colored = self.construct_ptn_links_colored()

    # parse structure & get molecule atoms and links
    def get_structure(self):

        # get molecule structure (transition matrix between atoms)
        buffer = self.molecule_entity.ChemicalStructures[0]['structure'].splitlines()
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
    def get_max_link_type(self):
        return max([int(type) for _, _, type in self.links])

    # delete all 'H' atoms from molecule (to speed up isomorphism detection algorithm)
    def delete_H_from_molecule(self):
        delete_atoms = []
        delete_links = []

        for i in range(0, len(self.atoms_id)):
            atom_name, atom_id = self.atoms_id[i]
            if atom_name == 'H':
                for j in range(0, len(self.links)):
                    atom_form, atom_to, link_type = self.links[j]
                    if atom_to == atom_id or atom_form == atom_id:
                        delete_links.append(j)
                delete_atoms.append(i)

        # delete atoms
        for x in delete_atoms:
            self.atoms_id = self.atoms_id[:x] + self.atoms_id[x+1:]

        # delete links
        for y in delete_links:
            self.links = self.links[:y] + self.links[y+1:]

        return self.atoms_id, self.links

    # get & classify molecule family
    def get_family(self):
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
        links_dictionary = self.get_links_dictionary()

        # get characteristics of molecules structure
        # 1 - check if molecule family = 'Halogenated compound'
        # check if atoms list contains one of these atoms ['F', 'Cl', 'Br', 'I' ]
        classification[7] = any(element for element in [atom in self.atoms for atom in ['F', 'Cl', 'Br', 'I']])

        # 2 - check if molecule family = 'Alkanes' or 'Alken'
        # check if atoms list contains only ['C', 'H']
        classification[10] = all(element for element in [atom in ['C', 'H'] for atom in self.atoms])
        # check if atoms list contains 'C' with multiple links
        if classification[10]:
            for link in self.links:
                if link[2] == '2':
                    classification[9] = True
                    break

        # 3 - check if molecule family = 'Alcohol'
        # check if atoms list contains [Atom : 'O']
        if any(atom == 'O' for atom in self.atoms):

            # check if links list contains at least [link : R-O-H ] for each atom 'O'
            for atom in self.atoms_id:
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
        if any(atom == 'N' for atom in self.atoms):
            # check if links list contains at least [link : R1-N, R2-N, R3-N] for each atom 'N'
            for atom in self.atoms_id:
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
            atom_name, _ = [atom for atom in self.atoms_id if atom[1] == atom_id][0]

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
        if self.isContains_cycle():
            classification[8] = True

        # return family after classification by order
        for i in range(len(classification)):
            if classification[i]:
                return families[i]

        # if any family is selected return 'Other'
        return families[-1]

    # create molecule dictionary {'atom_id' : ['neighbor1_id', 'neighbor2_id', ...], ... }
    def get_links_dictionary(self):
        links_dictionary = {}

        # sort atoms_id by there ID
        self.atoms_id.sort(key=lambda element: element[1])

        # complete the dictionary for each molecule with all its links
        for atom in self.atoms_id:
            atom_name, atom_id = atom
            links_dictionary[atom_id] = []

            for link in self.links:
                atom_from, atom_to, link_type = link

                # check if the atom 'atom_id' is part of the current 'link'
                if atom_to == atom_id or atom_from == atom_id:

                    # get linked atom id
                    if atom_from == atom_id:
                        linked_atom_id = atom_to
                    else:
                        linked_atom_id = atom_from

                    # get linked atom name from atoms_id list
                    linked_atom_name, _ = [atom for atom in self.atoms_id if atom[1] == linked_atom_id][0]

                    # append linked atom inside dictionary
                    links_dictionary[atom_id].append((linked_atom_id, linked_atom_name, int(link_type)))

        return links_dictionary

    # detect if molecule graph contains cycle (detect aromatic cycles for family classification)
    def isContains_cycle(self):
        # construct dictionary for each atom with its neighbors
        links_dictionary = {}
        for atom in self.atoms_id:
            _, atom_id = atom
            links_dictionary[atom_id] = []
            for link in self.links:
                from_id, to_id, _ = link
                if atom_id == from_id:
                    links_dictionary[atom_id].append(to_id)
                if atom_id == to_id:
                    links_dictionary[atom_id].append(from_id)

        # make in-depth course (DFS) for constructing graph & detecting cycles
        visited_nodes = []
        current_nodes = queue.Queue()
        current_nodes.put(self.atoms_id[0][1])

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

    # link coloring step : transform links (replace 2-link & 3-link with new atoms 'ZZZ')
    def transform_links_colored(self):

        # create new temporary atoms & links lists
        temp_atoms = [(atom_name, atom_id, '0') for atom_name, atom_id in self.atoms_id]
        temp_links = [(link_from, link_to, '0') for link_from, link_to, _ in self.links]

        # link coloring for 2-link & 3-link
        atom_id = len(self.atoms_id)
        for link in self.links:
            link_from, link_to, link_type = link

            # if link = double link 'link-2'
            if link_type == '2':
                # add one new atom 'ZZZ'
                temp_atoms.append(('ZZZ', atom_id, '1'))
                # add link from-ZZZ-to
                temp_links.append((link_from, atom_id, '1'))
                temp_links.append((link_to, atom_id, '1'))
                atom_id += 1

            # if link = triple link 'link-3'
            if link_type == '3':
                # add first new atoms 'ZZZ' with its links
                temp_atoms.append(('ZZZ', atom_id, '1'))
                temp_links.append((link_from, atom_id, '1'))
                last_atom_id = atom_id
                atom_id += 1

                # add second new atom 'ZZZ' with its links
                temp_atoms.append(('ZZZ', atom_id, '1'))
                temp_links.append((last_atom_id, atom_id, '1'))
                temp_links.append((atom_id, link_to, '1'))
                atom_id += 1

        return temp_atoms, temp_links

    # construct LAB
    def construct_lab(self):
        # sorting molecule atoms list & initialize temporary lists
        self.atoms_colored.sort()

        # construct Lab
        return [atom_id for _, atom_id, _ in self.atoms_colored]

    # construct PTN with 'ZZZ' (links colored) - arrays for isomorphism algorithm ('Nauty MCKAY')
    def construct_ptn_links_colored(self):
        # sorting molecule atoms list & initialize temporary lists
        self.atoms_colored.sort()
        ptn = []

        # construct lab_mol arrays
        lab_mol = [atom_name for atom_name, _, _ in self.atoms_colored]

        # construct PTN array
        toggle = True
        for i in range(1, len(lab_mol)):
            if lab_mol[i] == 'ZZZ' and toggle:
                ptn.append(0)
                toggle = False
            else:
                ptn.append(1)
        ptn.append(0)

        # transform PTN array to string
        temp = [str(elem) for elem in ptn]
        converted_ptn = ''.join(temp)

        return converted_ptn

    # construct PTN without 'ZZZ' (atoms coloration) - arrays for isomorphism algorithm ('Nauty MCKAY')
    def construct_ptn_atoms_colored(self):

        # sorting molecule atoms list & initialize temporary lists
        self.atoms_colored.sort()
        ptn = []

        # construct lab_mol arrays
        lab_mol = [atom_name for atom_name, _, _ in self.atoms_colored]

        # construct PTN array
        i = 1
        while i < len(lab_mol):
            if lab_mol[i - 1] == lab_mol[i]:
                ptn.append(1)
            else:
                ptn.append(0)
            i += 1
        ptn.append(0)

        # transform PTN array to string
        temp = [str(elem) for elem in ptn]
        converted_ptn = ''.join(temp)

        return converted_ptn

    # display molecule
    def display(self):
        print('---------------------------------------------------------------------')
        print('ID : ', self.id)
        print('NAME : ', self.name)
        print('FORMULA : ', self.formula)
        print('DIMENSIONS : ', self.dimension)
        print('COMPOSED : ', self.composed)
        print('FAMILY : ', self.family)
        print('ATOMS NUMBER : ', self.atoms_number)
        print('LINKS NUMBER : ', self.links_number)
        print('ATOMS : ', self.atoms)
        print('ATOMS_ID : ', self.atoms_id)
        print('LINKS : ', self.links)
        print('MAXIMUM_LINK_TYPE : ', self.maximum_link)
        print('ATOMS_NUMBER_TRANSFORMED : ', self.atoms_colored_number)
        print('LINKS_NUMBER_TRANSFORMED : ', self.links_colored_number)
        print('ATOMS_TRANSFORMED : ', self.atoms_colored)
        print('LINKS_TRANSFORMED : ', self.links_colored)
        print('LAB : ', self.lab)
        print('COLORED_ATOMS_PTN : ', self.ptn_atoms_colored)
        print('COLORED_LINKS_PTN : ', self.ptn_links_colored)
        print('---------------------------------------------------------------------')