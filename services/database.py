import mysql.connector
import models.molecule


class Database:

    # initialize database connexion
    def __init__(self):
        # initialize database
        self.connexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='molecular_isomorphism'
        )

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
        cursor = self.connexion.cursor()
        statement = "INSERT INTO `molecules`(`id_chebi`, `name`, `formula`, `dimension`, `family`, `maximum_link`, " \
                    "`atoms_number`, `links_number`, `atoms`, `links`, `colored_atoms_number`, `colored_links_number`, " \
                    "`atoms_colored`, `links_colored`, `canonical_form1`, `canonical_form2`, " \
                    "`canonical_form3`, `canonical_label1`, `canonical_label2`, `canonical_label3`) VALUES (" \
                    f" '{molecule.id}', '{molecule.name}', '{molecule.formula}'," \
                    f" '{molecule.dimension}', '{molecule.family}', {molecule.maximum_link}," \
                    f" {molecule.atoms_number}, {molecule.links_number}, '{self.str_list(molecule.atoms_id)}', '{self.str_list(molecule.links)}'," \
                    f" {molecule.atoms_colored_number}, {molecule.links_colored_number}," \
                    f" '{self.str_list(molecule.atoms_colored)}', '{self.str_list(molecule.links_colored)}'," \
                    f" NULL, NULL, NULL, NULL, NULL, NULL)"
        cursor.execute(statement)
        self.connexion.commit()

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
        cursor.execute("TRUNCATE TABLE molecules")
        cursor.execute("TRUNCATE TABLE links")
        cursor.execute("TRUNCATE TABLE lab")
        cursor.execute("TRUNCATE TABLE ptn")
        self.connexion.commit()

    # delete one molecule by ID
    def delete_molecule(self, molecule_id):
        cursor = self.connexion.cursor()
        statement = f"DELETE FROM `molecules` WHERE id_chebi = '{molecule_id}'"
        cursor.execute(statement)
        self.connexion.commit()
        print(f"Molecule '{molecule_id}' deleted successfully")
