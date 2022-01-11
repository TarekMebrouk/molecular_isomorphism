import mysql.connector
from models.molecule import *


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

        # 2- save molecule atoms
        self.save_atoms(molecule)

        # 3- save molecule links
        self.save_links(molecule)

        # 4- save molecule lab & ptn
        self.save_ptn_lab(molecule)

        print(f"Molecule '{molecule.id}' saved successfully")

    # save molecule information
    def save_molecule_information(self, molecule):
        cursor = self.connexion.cursor()
        statement = "INSERT INTO `molecules`(`id_chebi`, `name`, `formula`, `dimension`, " \
                    "`family`, `atoms_number`, `links_number`, `maximum_link`, " \
                    "`transformed_atoms_number`, `transformed_links_number`, `canonical_form1`, " \
                    "`canonical_form2`, `canonical_form3`, `canonical_form4`) VALUES (" \
                    f" '{molecule.id}', '{molecule.name}', '{molecule.formula}'," \
                    f" '{molecule.dimension}', '{molecule.family}', {molecule.atoms_number}," \
                    f" {molecule.links_number}, {molecule.maximum_link}," \
                    f" {molecule.atoms_transformed_number}, {molecule.links_transformed_number}," \
                    f" NULL, NULL, NULL, NULL)"
        cursor.execute(statement)
        self.connexion.commit()

    # save molecule atoms to database
    def save_atoms(self, molecule):
        cursor = self.connexion.cursor()
        for atom in molecule.atoms_transformed:
            atom_name, atom_id, type_c = atom
            statement = "INSERT INTO `atoms`(`id`, `id_chebi`, `atom_name`, `atom_id`, `ctype`) VALUES (" \
                        f"NULL, '{molecule.id}', '{atom_name}', {atom_id}, {type_c})"
            cursor.execute(statement)
            self.connexion.commit()

    # save molecule links to database
    def save_links(self, molecule):
        cursor = self.connexion.cursor()
        for link in molecule.links_transformed:
            atom_from, atom_to, type_c = link
            statement = "INSERT INTO `links`(`id`, `id_chebi`, `atom_from`, `atom_to`, `ctype`) VALUES (" \
                        f"NULL, '{molecule.id}', {atom_from}, {atom_to}, {type_c})"
            cursor.execute(statement)
            self.connexion.commit()

    # save molecule lab & ptn to database
    def save_ptn_lab(self, molecule):
        cursor = self.connexion.cursor()

        # save lab array
        statement = f"INSERT INTO `lab`(`id`, `id_chebi`, `lab`) VALUES (NULL, '{molecule.id}', '{molecule.lab}')"
        cursor.execute(statement)
        self.connexion.commit()

        # save ptn array
        statement = f"INSERT INTO `ptn`(`id`, `id_chebi`, `ptn`) VALUES (NULL, '{molecule.id}', '{molecule.ptn}')"
        cursor.execute(statement)
        self.connexion.commit()

    # clear all rows inside database tables
    def clear_tables(self):
        cursor = self.connexion.cursor()
        cursor.execute("TRUNCATE TABLE molecules")
        cursor.execute("TRUNCATE TABLE atoms")
        cursor.execute("TRUNCATE TABLE links")
        cursor.execute("TRUNCATE TABLE lab")
        cursor.execute("TRUNCATE TABLE ptn")
        self.connexion.commit()
