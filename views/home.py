from services.database import *
from views.graph import *
import streamlit as st

# constants
families = ['All', 'Amide', 'Amine', 'Ester', 'Carboxylic acid', 'Ketone', 'Aldehyde', 'Alcohol', 'Halogenated compound', 'Aromatic compound', 'Alken', 'Alkanes', 'Other']
molecules_type = ['All', 'single', 'double', 'triple']


class Home:

    # init web-page architecture
    def __init__(self):

        # initialise state variables (session)
        if 'selected_molecule_id' not in st.session_state:
            st.session_state.selected_molecule_id = ''
        if 'search_molecule_id' not in st.session_state:
            st.session_state.search_molecule_id = ''
        if 'selected_family' not in st.session_state:
            st.session_state.selected_family = families[0]
        if 'selected_molecule_type' not in st.session_state:
            st.session_state.selected_molecule_type = 'All'
        if 'selected_molecule_name' not in st.session_state:
            st.session_state.selected_molecule_name = ''
        if 'selected_molecule_formula' not in st.session_state:
            st.session_state.selected_molecule_formula = ''

        # page sections & settings
        st.set_page_config(layout="wide")
        header = st.container()
        statistics = st.container()
        sidebar = st.container()
        molecules_list = st.container()
        single_molecule = st.container()

        # check if any molecule is selected
        molecule_id = st.session_state.selected_molecule_id
        if molecule_id != '':
            # single molecule display
            with single_molecule:
                self.single_molecule(molecule_id)
        else:
            # application header (Logo + Title)
            with header:
                self.header()

            # application statistics (Charts/Graphs)
            with statistics:
                self.statistics()

            # application sidebar (filters & search)
            with sidebar:
                self.sidebar()

            # molecules list
            with molecules_list:
                self.molecules_list()

    # Header section
    @staticmethod
    def header():
        col1, mid, col2 = st.columns([10, 3, 50])
        with col1:
            st.image('assets/logo.png', width=80)
        with col2:
            st.header('Molecular isomorphism')

    # Statistics section
    def statistics(self):

        # display families statistics
        st.subheader('Families statistics')
        self.bar_chart_families_count()

        # display isomorphism statistics
        st.subheader('Isomorphism statistics')

        col1, _, col2 = st.columns([50, 1, 49])
        # isomorphism by version
        with col1:
            self.pie_chart_isomorphism_byVersion()
        # isomorphism by family
        with col2:
            self.pie_chart_isomorphism_byFamily()

    # sidebar section
    def sidebar(self):
        with st.sidebar.container():
            # get all molecules data
            molecules = self.get_data()

            # display title
            st.header('Search filters')

            # search molecule by ChEBI ID
            molecules_id_list = [''] + [molecule[0] for molecule in molecules]
            st.session_state.search_molecule_id = st.selectbox(label='Search for a molecule',
                                                               index=0,
                                                               options=molecules_id_list)

            # select family section
            st.session_state.selected_family = st.selectbox(label='Select molecules family',
                                                            index=0,
                                                            options=families)

            # select molecules types (single/double/triple link)
            st.session_state.selected_molecule_type = st.selectbox(label='Select molecules links type',
                                                                   index=0,
                                                                   options=molecules_type)

            # search molecules by name
            molecules_names = [''] + [molecule[2] for molecule in molecules]
            st.session_state.selected_molecule_name = st.selectbox(label='Search molecule by name',
                                                                   index=0,
                                                                   options=molecules_names)
            if st.session_state.selected_molecule_name != '':
                for molecule in molecules:
                    if molecule[2] == st.session_state.selected_molecule_name:
                        st.session_state.search_molecule_id = molecule[0]
                        break

            # search molecules by formula
            molecules_formula = [''] + [molecule[3] for molecule in molecules]
            st.session_state.selected_molecule_formula = st.selectbox(label='Search molecule by formula',
                                                                      index=0,
                                                                      options=molecules_formula)
            if st.session_state.selected_molecule_formula != '':
                for molecule in molecules:
                    if molecule[3] == st.session_state.selected_molecule_formula:
                        st.session_state.search_molecule_id = molecule[0]
                        break

    # Single molecule section
    @staticmethod
    def single_molecule(molecule_id):

        # get all molecule data
        database_service = Database()
        molecule = database_service.get_single_molecule(molecule_id)

        # get molecules with identical structure (compared with all or only Family)
        isomorphism_all_version1 = database_service.get_molecules_isomorphism_withAll(molecule_id, version=1)
        isomorphism_all_version2 = database_service.get_molecules_isomorphism_withAll(molecule_id, version=2)
        isomorphism_all_version3 = database_service.get_molecules_isomorphism_withAll(molecule_id, version=3)

        isomorphism_family_version1 = database_service.get_molecules_isomorphism_withFamily(molecule_id, version=1)
        isomorphism_family_version2 = database_service.get_molecules_isomorphism_withFamily(molecule_id, version=2)
        isomorphism_family_version3 = database_service.get_molecules_isomorphism_withFamily(molecule_id, version=3)

        # handler function
        def back_handler():
            st.session_state.selected_molecule_id = ''

        # display return button
        st.button(key=200, label='⮌ back', on_click=back_handler)

        # -1- display title of molecule information
        st.subheader('Molecule information')

        # display molecule information
        col1, _, col2 = st.columns([50, 1, 49])

        # left side : display molecule data (name, formula, family, maximum_link, number_isomorphism)
        with col1:
            st.markdown(f'**CHEBI ID** : {molecule.id}')
            st.markdown(f'**Name** : {molecule.name}')
            st.markdown(f'**Formula** : {molecule.formula}')
            st.markdown(f'**Family** : {molecule.family}')
            st.markdown('**Star** : ⭐⭐⭐')
            st.markdown(f'**Atoms count** : {molecule.atoms_number}')
            st.markdown(f'**Links count** : {molecule.links_number}')

        # right side : display molecule structure
        with col2:
            st.markdown(f'**Link type** : {molecule.maximum_link}')
            st.markdown(f'**Colored atoms count** : {molecule.atoms_colored_number}')
            st.markdown(f'**Colored links count** : {molecule.links_colored_number}')
            total_count = len(isomorphism_all_version1 + isomorphism_all_version2 + isomorphism_all_version3)
            st.markdown(f'**Isomorphism total count** : {total_count}')
            st.markdown('**Isomorphism with all** : '
                        f'*v1*: {len(isomorphism_all_version1)}, '
                        f'*v2*: {len(isomorphism_all_version2)}, '
                        f'*v3*: {len(isomorphism_all_version3)}')
            st.markdown('**Isomorphism with same family** : '
                        f'*v1*: {len(isomorphism_family_version1)}, '
                        f'*v2*: {len(isomorphism_family_version2)}, '
                        f'*v3*: {len(isomorphism_family_version3)}')

        # display title of molecular structures
        st.subheader('Molecular structures')

        # display molecule structures (before and after transformation 'coloration')
        col1, _, col2 = st.columns([50, 1, 49])

        # left side : display molecular structure before transformation
        graph = Graph(molecule)
        with col1:
            st.markdown('**Before transformation**')
            graph.simple()

        # right side : display molecular structure after transformation (coloration of atoms and links)
        with col2:
            st.markdown('**After transformation**')
            graph.advanced()

    # Molecules list section
    def molecules_list(self):

        # get molecules IDs filtered
        molecules = self.get_filtered_molecules_list()

        # display molecules list
        if molecules is not None:

            # display title
            st.subheader('Molecules list')
            st.caption(f' {len(molecules)} selected molecules')

            # display list of molecules (ChEBI IDs)
            count = 1
            for molecule_id in molecules:
                with st.expander(molecule_id):
                    self.molecule_expanded(molecule_id, count)  # display expanded molecule item
                    count += 1

    # molecule expanded item section
    @staticmethod
    def molecule_expanded(molecule_id, index):
        col1, _, col2, _, col3 = st.columns([40, 1, 38, 1, 20])

        # get molecule data
        database_service = Database()
        molecule = database_service.get_single_molecule(molecule_id)

        # get count of molecule isomorphism with molecule_id
        isomorphism_count = database_service.get_count_isomorphism_byId(molecule_id)

        # left side : display molecule data
        with col1:
            st.markdown(f'**Name** : {molecule.name}')
            st.markdown(f'**Formula** : {molecule.formula}')
            st.markdown(f'**Family** : {molecule.family}')
            st.markdown(f'**Link type** : {molecule.maximum_link}')

        # middle side : display molecule data
        with col2:
            st.markdown(f'**Atoms count** : {molecule.atoms_number}')
            st.markdown(f'**Links count** : {molecule.links_number}')
            st.markdown(f'**Isomorphism count** : {isomorphism_count}')

        # handler function
        def next_handler():
            st.session_state.selected_molecule_id = molecule_id

        # right side : display button
        with col3:
            st.button(key=100 + index, label='more details', on_click=next_handler)

    # get all molecules IDs
    @st.cache
    def get_data(self):
        # init database connexion
        database_service = Database()

        # get molecules IDs
        return database_service.get_molecules_ids()

    # get molecules IDs list filtered by (family, link type)
    def get_filtered_molecules_list(self):
        # get all molecules IDs
        molecules = self.get_data()
        molecules_filtered = []
        if molecules is not None:
            # filter list by molecule family
            if st.session_state.selected_family != 'All':
                molecules_filtered = [molecule[0] for molecule in molecules
                                      if molecule[1] == st.session_state.selected_family]
            else:
                molecules_filtered = [molecule[0] for molecule in molecules]

            # filter list by molecule link type
            if st.session_state.selected_molecule_type != 'All':
                molecules_filtered = [molecule[0] for molecule in molecules
                                      if int(molecule[4]) == molecules_type.index(st.session_state.selected_molecule_type)]

            # search molecule IDs
            if st.session_state.search_molecule_id != '':
                molecules_filtered = [st.session_state.search_molecule_id]

        return molecules_filtered

    # display pie chart of isomorphism by version
    @staticmethod
    def pie_chart_isomorphism_byVersion():
        # get count isomorphism by version
        version_1, version_2, version_3 = Database().get_count_isomorphism_byVersion()

        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        labels = 'Simple', 'Atom colored', 'Link colored'
        total = version_1 + version_2 + version_3
        st.markdown(f'**Total isomorphism : ** : {total}')
        if total != 0:
            sizes = [version_1 * 100 / total, version_2 * 100 / total, version_3 * 100 / total]
            explode = (0.1, 0, 0)

            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            st.pyplot(fig1)

    # display bar chart of families molecules count
    @staticmethod
    def bar_chart_families_count():
        # get families molecules count
        family_dict = Database().get_count_family()
        st.caption(f'**Total molecules : ** {sum(list(family_dict.values()))}')

        fig = plt.figure(figsize=(10, 5))

        plt.barh(list(family_dict.keys()), list(family_dict.values()))
        plt.ylabel("Molecular families")
        plt.xlabel("Number of molecules")
        st.pyplot(fig)

    # display pie chart of isomorphism by version
    @staticmethod
    def pie_chart_isomorphism_byFamily():
        # get count isomorphism by family
        family_dict = Database().get_count_isomorphism_byFamily()

        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        labels = list(family_dict.keys())
        total = sum(list(family_dict.values()))
        st.markdown('')
        if total != 0:
            sizes = list(family_dict.values())

            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            st.pyplot(fig1)
