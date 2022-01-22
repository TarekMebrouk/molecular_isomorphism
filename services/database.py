from models.molecule import *
import mysql.connector
import json


class Database:

    # initialize database connexion
    def __init__(self):
        # get database connexion configuration from JSON file
        # Opening JSON file
        config_file = open('config.json')
        configuration = json.load(config_file)

        # initialize database connexion
        self.connexion = mysql.connector.connect(
            host=configuration['database']['host'],
            user=configuration['database']['user'],
            password=configuration['database']['password'],
            database=configuration['database']['name']
        )

        # close JSON file
        config_file.close()

    # save molecule to database
    def save_molecule(self, molecule):
        # 1- save molecule information
        self.save_molecule_information(molecule)

        # 3- save molecule links
        self.save_links(molecule)

        # 4- save molecule lab & ptn
        self.save_ptn_lab(molecule)

        print(f"Molecule '{molecule.id}' saved successfully")

    # save molecule information
    def save_molecule_information(self, molecule):
        # remove special characters from molecule information (delete ' from string)
        molecule = self.remove_special_chars(molecule)
        cursor = self.connexion.cursor()
        statement = "INSERT INTO `molecules`(`id_chebi`, `name`, `formula`, `dimension`, `family`, `maximum_link`, " \
                    "`atoms_number`, `links_number`, `atoms`, `links`, `colored_atoms_number`, `colored_links_number`, " \
                    "`atoms_colored`, `links_colored`) VALUES (" \
                    f" '{molecule.id}', '{molecule.name}', '{molecule.formula}'," \
                    f" '{molecule.dimension}', '{molecule.family}', {molecule.maximum_link}," \
                    f" {molecule.atoms_number}, {molecule.links_number}, '{self.str_list(molecule.atoms_id)}', '{self.str_list(molecule.links)}'," \
                    f" {molecule.atoms_colored_number}, {molecule.links_colored_number}," \
                    f" '{self.str_list(molecule.atoms_colored)}', '{self.str_list(molecule.links_colored)}')"
        cursor.execute(statement)
        self.connexion.commit()

    # transform molecule information to safe (delete {'} from information to skip SQL exception)
    @staticmethod
    def remove_special_chars(molecule):

        molecule.id = str(molecule.id).replace("'", "")
        molecule.formula = str(molecule.formula).replace("'", "")
        molecule.name = str(molecule.name).replace("'", "")
        molecule.dimension = str(molecule.dimension).replace("'", "")

        return molecule

    # transform list [('C', 0, 1), ...] to string (for fetching data into database)
    @staticmethod
    def str_list(list):
        converted_list = ''
        for line in list:
            for i in range(len(line)):
                converted_list += f'{line[i]}'
                if i == len(line) - 1:
                    converted_list += '|'
                else:
                    converted_list += ','
        return converted_list

    # save molecule links to database
    def save_links(self, molecule):
        cursor = self.connexion.cursor()
        # save first version links (without colored links)
        for link in molecule.links:
            atom_from, atom_to, _ = link
            statement = "INSERT INTO `links`(`id`, `id_chebi`, `atom_from`, `atom_to`, `version`) VALUES (" \
                        f"NULL, '{molecule.id}', {atom_from}, {atom_to}, 0)"
            cursor.execute(statement)
            self.connexion.commit()

        # save second version links (colored links)
        for link in molecule.links_colored:
            atom_from, atom_to, _ = link
            statement = "INSERT INTO `links`(`id`, `id_chebi`, `atom_from`, `atom_to`, `version`) VALUES (" \
                        f"NULL, '{molecule.id}', {atom_from}, {atom_to}, 1)"
            cursor.execute(statement)
            self.connexion.commit()

    # save molecule lab & ptn to database
    def save_ptn_lab(self, molecule):
        cursor = self.connexion.cursor()

        # save lab array
        index = 0
        for lab_item in molecule.lab:
            ctype = [ctype for atom_name, atom_id, ctype in molecule.atoms_colored if atom_id == lab_item][0]
            statement = f"INSERT INTO `lab`(`id`, `id_chebi`, `atom_id`, `index`, `ctype`) VALUES (" \
                        f"NULL, '{molecule.id}', {lab_item}, {index}, {ctype})"
            cursor.execute(statement)
            self.connexion.commit()
            index += 1

        # save ptn for colored atoms - version = 0
        statement = f"INSERT INTO `ptn`(`id`, `id_chebi`, `ptn`, `version`) VALUES (NULL, '{molecule.id}', '{molecule.ptn_atoms_colored}', 0)"
        cursor.execute(statement)
        self.connexion.commit()

        # save ptn for colored links - version = 1
        statement = f"INSERT INTO `ptn`(`id`, `id_chebi`, `ptn`, `version`) VALUES (NULL, '{molecule.id}', '{molecule.ptn_links_colored}', 1)"
        cursor.execute(statement)
        self.connexion.commit()

    # clear all rows inside database tables
    def clear_tables(self):
        cursor = self.connexion.cursor()
        cursor.execute("DELETE FROM `molecules`")
        self.connexion.commit()

    # delete one molecule by ID
    def delete_molecule(self, molecule_id):
        cursor = self.connexion.cursor()
        statement = f"DELETE FROM `molecules` WHERE id_chebi = '{molecule_id}'"
        cursor.execute(statement)
        self.connexion.commit()
        print(f"Molecule '{molecule_id}' deleted successfully")

    # get all molecules
    def get_molecules(self):
        molecules = []
        cursor = self.connexion.cursor()
        cursor.execute("SELECT * FROM molecules")
        result_set = cursor.fetchall()
        for row in result_set:
            molecules.append(Molecule(row))

        return molecules

    # get all molecules ChEBI IDs identical structure
    def get_molecules_isomorphism_withAll(self, molecule_id, version=1):
        # prepare statement
        cursor = self.connexion.cursor()
        statement = "SELECT m2.id_chebi from molecules m1, molecules m2 WHERE "

        # check of comparison version
        if version == 1:  # compare canonical form 1
            statement += "m1.canonical_form1 = m2.canonical_form1 "

        if version == 2:  # compare canonical form 2
            statement += "m1.canonical_form2 = m2.canonical_form2 "

        if version == 3:  # compare canonical form 3
            statement += "m1.canonical_form3 = m2.canonical_form3 "

        # execute statement & fetch information
        statement += f"and m1.id_chebi != m2.id_chebi and m1.id_chebi = '{molecule_id}'"
        cursor.execute(statement)
        result_set = cursor.fetchall()

        return [row[0] for row in result_set]

    # get all molecules ChEBI IDs identical structure
    def get_molecules_isomorphism_withFamily(self, molecule_id, version=1):
        # prepare statement
        cursor = self.connexion.cursor()
        statement = "SELECT m2.id_chebi from molecules m1, molecules m2 WHERE " \
                    f"m1.family = m2.family and "

        # check of comparison version
        if version == 1:  # compare canonical form 1
            statement += "m1.canonical_form1 = m2.canonical_form1 "

        if version == 2:  # compare canonical form 2
            statement += "m1.canonical_form2 = m2.canonical_form2 "

        if version == 3:  # compare canonical form 3
            statement += "m1.canonical_form3 = m2.canonical_form3 "

        # execute statement & fetch information
        statement += f"and m1.id_chebi != m2.id_chebi and m1.id_chebi = '{molecule_id}'"
        cursor.execute(statement)
        result_set = cursor.fetchall()

        return [row[0] for row in result_set]

    # count isomorphism of each comparison version (canonical form [1, 2, 3])
    def get_count_isomorphism_byVersion(self):
        # prepare statement
        cursor = self.connexion.cursor()
        statement_1 = "SELECT count(m1.id_chebi) from molecules m1, molecules m2 " \
                      "WHERE m1.canonical_form1 = m2.canonical_form1 and m1.id_chebi != m2.id_chebi"

        statement_2 = "SELECT count(m1.id_chebi) from molecules m1, molecules m2 " \
                      "WHERE m1.canonical_form2 = m2.canonical_form2 and m1.id_chebi != m2.id_chebi"

        statement_3 = "SELECT count(m1.id_chebi) from molecules m1, molecules m2 " \
                      "WHERE m1.canonical_form3 = m2.canonical_form3 and m1.id_chebi != m2.id_chebi"

        # execute statement & fetch information
        cursor.execute(statement_1)
        count_1 = int(cursor.fetchall()[0][0]) / 2

        cursor.execute(statement_2)
        count_2 = int(cursor.fetchall()[0][0]) / 2

        cursor.execute(statement_3)
        count_3 = int(cursor.fetchall()[0][0]) / 2

        return int(count_1), int(count_2), int(count_3)

    # count molecules inside each molecular family
    def get_count_family(self):
        cursor = self.connexion.cursor()

        families = ['Amide', 'Amine', 'Ester', 'Carboxylic acid', 'Ketone', 'Aldehyde', 'Alcohol',
                    'Halogenated compound', 'Aromatic compound', 'Alken', 'Alkanes', 'Other']
        family_counter = {}

        for family in families:
            cursor.execute(f"SELECT count(id_chebi) from molecules WHERE family = '{family}'")
            family_counter[family] = int(cursor.fetchall()[0][0])

        return family_counter

    # count number molecules isomorphism with 'molecule_id'
    def get_count_isomorphism_byId(self, molecule_id):
        # prepare statement
        cursor = self.connexion.cursor()
        statement_1 = "SELECT count(m1.id_chebi) from molecules m1, molecules m2 " \
                      "WHERE m1.canonical_form1 = m2.canonical_form1 and m1.id_chebi != m2.id_chebi " \
                      f"and m1.id_chebi = '{molecule_id}'"

        statement_2 = "SELECT count(m1.id_chebi) from molecules m1, molecules m2 " \
                      "WHERE m1.canonical_form2 = m2.canonical_form2 and m1.id_chebi != m2.id_chebi " \
                      f"and m1.id_chebi = '{molecule_id}'"

        statement_3 = "SELECT count(m1.id_chebi) from molecules m1, molecules m2 " \
                      "WHERE m1.canonical_form3 = m2.canonical_form3 and m1.id_chebi != m2.id_chebi " \
                      f"and m1.id_chebi = '{molecule_id}'"

        # execute statement & fetch information
        cursor.execute(statement_1)
        count_1 = int(cursor.fetchall()[0][0])

        cursor.execute(statement_2)
        count_2 = int(cursor.fetchall()[0][0])

        cursor.execute(statement_3)
        count_3 = int(cursor.fetchall()[0][0])

        return count_1 + count_2 + count_3

    # count isomorphism by family
    def get_count_isomorphism_byFamily(self):
        cursor = self.connexion.cursor()

        families = ['Amide', 'Amine', 'Ester', 'Carboxylic acid', 'Ketone', 'Aldehyde', 'Alcohol',
                    'Halogenated compound', 'Aromatic compound', 'Alken', 'Alkanes', 'Other']
        family_counter = {}

        for family in families:
            cursor.execute("SELECT count(m1.id_chebi) from molecules m1, molecules m2 "
                           "WHERE m1.canonical_form1 = m2.canonical_form1 and m1.id_chebi != m2.id_chebi "
                           f"and m1.family = m2.family and m1.family = '{family}'")
            family_counter[family] = int(cursor.fetchall()[0][0])

        return family_counter

    # get all molecules IDs with families
    def get_molecules_ids(self):
        molecules = []
        cursor = self.connexion.cursor()
        cursor.execute("SELECT id_chebi, family, name, formula, maximum_link FROM molecules")
        result_set = cursor.fetchall()
        for row in result_set:
            molecules.append(row)

        return molecules

    # get single molecule data by ID
    def get_single_molecule(self, molecule_id):
        cursor = self.connexion.cursor()
        cursor.execute(f"SELECT * FROM molecules WHERE id_chebi = '{molecule_id}'")

        return Molecule(cursor.fetchall()[0])
