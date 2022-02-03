from services.database import *
from views.graph import *
import streamlit as st

# constants
families = ['All', 'Amide', 'Amine', 'Ester', 'Carboxylic acid', 'Ketone', 'Aldehyde', 'Alcohol', 'Halogenated compound', 'Aromatic compound', 'Alken', 'Alkanes', 'Other']
molecules_type = ['All', 'single', 'double', 'triple']
comparison_type = ['All', 'Family']
comparison_version = ['Version 1', 'Version 2', 'Version 3', 'version 4']


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
        if 'selected_comparison_type' not in st.session_state:
            st.session_state.selected_comparison_type = 'All'
        if 'selected_comparison_version' not in st.session_state:
            st.session_state.selected_comparison_version = 'All'
        if 'selected_comparison_molecule_id' not in st.session_state:
            st.session_state.selected_comparison_molecule_id = ''
        if 'pagination_start' not in st.session_state:
            st.session_state.pagination_start = 0
        if 'statistics_state' not in st.session_state:
            st.session_state.statistics_state = False

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
                pass

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
        col1, _, col2 = st.columns([90, 5, 5])
        with col1:
            st.subheader('Statistics')
        with col2:
            st.write('')
            st.session_state.statistics_state = st.checkbox('')

        # if statistics section is activated
        if st.session_state.statistics_state:

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

            # handler search filters
            def handler_search_filters():
                st.session_state.pagination_start = 0

            # search molecule by ChEBI ID
            value = st.text_input('Search for a molecule', '')
            if value != '' and value in [molecule[0] for molecule in molecules]:
                st.session_state.search_molecule_id = value
                handler_search_filters()
            else:
                st.session_state.search_molecule_id = ''

            # select family section
            st.session_state.selected_family = st.selectbox(label='Select molecules family',
                                                            index=0,
                                                            options=families,
                                                            on_change=handler_search_filters)

            # select molecules types (single/double/triple link)
            st.session_state.selected_molecule_type = st.selectbox(label='Select molecules links type',
                                                                   index=0,
                                                                   options=molecules_type,
                                                                   on_change=handler_search_filters)

            # search molecules by name
            molecules_names = [''] + [molecule[2] for molecule in molecules]
            st.session_state.selected_molecule_name = st.selectbox(label='Search molecule by name',
                                                                   index=0,
                                                                   options=molecules_names,
                                                                   on_change=handler_search_filters)
            if st.session_state.selected_molecule_name != '':
                for molecule in molecules:
                    if molecule[2] == st.session_state.selected_molecule_name:
                        st.session_state.search_molecule_id = molecule[0]
                        break

            # search molecules by formula
            molecules_formula = [''] + [molecule[3] for molecule in molecules]
            st.session_state.selected_molecule_formula = st.selectbox(label='Search molecule by formula',
                                                                      index=0,
                                                                      options=molecules_formula,
                                                                      on_change=handler_search_filters)
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
            st.session_state.statistics_state = False
            st.session_state.selected_molecule_id = ''

        # display return button
        st.button(key=200, label='⮌ back', on_click=back_handler)

        # -1- display title of molecule information
        st.subheader('Molecule information')

        # display molecule information
        col1, _, col2 = st.columns([50, 1, 49])

        # left side : display molecule data (name, formula, family, maximum_link, number_isomorphism)
        with col1:
            st.markdown(f'**CHEBI ID : ** {molecule.id}')
            st.markdown(f'**Name : ** {molecule.name}')
            st.markdown(f'**Formula : ** {molecule.formula}')
            st.markdown(f'**Family : ** {molecule.family}')
            st.markdown('**Star : ** ⭐⭐⭐')
            st.markdown(f'**Dimension : ** {molecule.dimension}')
            st.markdown(f'**Atoms count : ** {molecule.atoms_number}')

        # right side : display molecule structure
        with col2:
            st.markdown(f'**Links count : ** {molecule.links_number}')
            st.markdown(f'**Link type : ** {molecule.maximum_link}')
            st.markdown(f'**Colored atoms count : ** {molecule.atoms_colored_number}')
            st.markdown(f'**Colored links count : ** {molecule.links_colored_number}')
            total_count = len(isomorphism_all_version1 + isomorphism_all_version2 + isomorphism_all_version3)
            st.markdown(f'**Isomorphism total count : ** {total_count}')
            st.markdown('**Isomorphism with all : ** '
                        f'*v1*: {len(isomorphism_all_version1)}, '
                        f'*v2*: {len(isomorphism_all_version2)}, '
                        f'*v3*: {len(isomorphism_all_version3)}')
            st.markdown('**Isomorphism with same family : ** '
                        f'*v1*: {len(isomorphism_family_version1)}, '
                        f'*v2*: {len(isomorphism_family_version2)}, '
                        f'*v3*: {len(isomorphism_family_version3)}')

        # display title of molecular structures
        st.subheader('Molecular structures')

        # display molecule structures (before and after transformation 'coloration')
        col1, _, col2 = st.columns([50, 1, 49])

        # left side : display molecular structure before transformation
        principal_graph = Graph(molecule)
        with col1:
            st.markdown('**Before transformation**')
            principal_graph.simple()

        # right side : display molecular structure after transformation (coloration of atoms and links)
        with col2:
            st.markdown('**After transformation**')
            principal_graph.advanced()

        # display title of isomorphism section
        st.subheader('Molecular isomorphism')

        # display menu filter (select :: Family & Version & ChEBI ID)
        col1, _, col2, _, col3 = st.columns([24, 1, 25, 1, 49])

        with col1:  # select comparison type (with all, by family)
            st.session_state.selected_comparison_type = st.selectbox(label='Select comparison type',
                                                                     index=0,
                                                                     options=comparison_type)

        with col2:  # select comparison type (all, version 1, version 2, version 3)
            st.session_state.selected_comparison_version = st.selectbox(label='Select comparison version',
                                                                        index=0,
                                                                        options=comparison_version)

        # get all isomorphism molecules filtered by comparison version & family
        isomorphism_molecules = database_service.get_molecules_isomorphism(molecule_id=molecule_id,
                                                                           comparison_type=st.session_state.selected_comparison_type,
                                                                           comparison_version=comparison_version.index(st.session_state.selected_comparison_version) + 1)

        with col3:  # search molecule isomorphism by ChEBI ID
            molecules_isomorphism = [''] + [id for id in isomorphism_molecules]
            st.session_state.selected_comparison_molecule_id = st.selectbox(label='Search molecule by ChEBI ID',
                                                                            index=0,
                                                                            options=molecules_isomorphism)

        # display molecular structure comparison
        st.caption(f'{len(isomorphism_molecules)} molecules found\n')
        if st.session_state.selected_comparison_molecule_id != '':
            # get selected molecule information
            selected_molecule = database_service.get_single_molecule(st.session_state.selected_comparison_molecule_id)

            # write some information about selected molecule structure
            # display molecule information
            col1, _, col2, _, col3 = st.columns([33, 1, 31, 1, 33])

            # left side
            with col1:
                st.markdown(f'**Name : ** {selected_molecule.name}')
                st.markdown(f'**Formula : ** {selected_molecule.formula}')
                st.markdown(f'**Family : ** {selected_molecule.family}')

            # middle side
            with col2:
                st.markdown(f'**Atoms count : ** {selected_molecule.atoms_number}')
                st.markdown(f'**Links count : ** {selected_molecule.links_number}')

            # right side
            with col3:
                st.markdown(f'**Colored atoms count : ** {selected_molecule.atoms_colored_number}')
                st.markdown(f'**Colored links count : ** {selected_molecule.links_colored_number}')

            # display selected molecule structure compared to the principal molecule
            col1, _, col2 = st.columns([50, 1, 49])

            second_graph = Graph(selected_molecule)
            with col1:
                st.markdown('**Principal molecule**')
                if st.session_state.selected_comparison_version == 'Version 1':
                    principal_graph.simple()
                else:
                    principal_graph.advanced()
            with col2:
                st.markdown('**Molecule to compare**')
                if st.session_state.selected_comparison_version == 'Version 1':
                    second_graph.simple()
                else:
                    second_graph.advanced()
        else:
            st.caption('no molecules have been selected')

    # Molecules list section
    def molecules_list(self):

        # get molecules IDs filtered
        molecules = self.get_filtered_molecules_list()

        # display molecules list
        if molecules is not None:

            # pagination step
            pagination_max = 50
            if st.session_state.pagination_start + pagination_max > len(molecules):
                pagination_end = len(molecules)
            else:
                pagination_end = st.session_state.pagination_start + pagination_max
            molecules_pagination = molecules[st.session_state.pagination_start:pagination_end]

            # display title
            st.subheader('Molecules list')
            st.caption(f' {len(molecules)} selected molecules')
            st.caption(f' {st.session_state.pagination_start}-{pagination_end}/{len(molecules)} displayed molecules')

            # display list of molecules (ChEBI IDs)
            count = 1
            for molecule_id in molecules_pagination:
                with st.expander(molecule_id):
                    self.molecule_expanded(molecule_id, count)  # display expanded molecule item
                    count += 1

            # display pagination buttons
            col1, _, col2 = st.columns([10, 80, 10])

            # back button
            with col1:
                # handler function
                def back_pagination_handler():
                    st.session_state.pagination_start -= pagination_max

                # display back pagination button
                disabled = False
                if st.session_state.pagination_start == 0:
                    disabled = True
                st.button(key=100000, label='← back', on_click=back_pagination_handler, disabled=disabled)

            # next button
            with col2:
                # handler function
                def next_pagination_handler():
                    st.session_state.pagination_start += pagination_max

                # display next pagination button
                disabled = False
                if pagination_end >= len(molecules):
                    disabled = True
                st.button(key=100001, label='next →', on_click=next_pagination_handler, disabled=disabled)

    # molecule expanded item section
    @staticmethod
    def molecule_expanded(molecule_id, index):
        col1, _, col2, _, col3 = st.columns([40, 1, 38, 1, 20])

        # get molecule data
        database_service = Database()
        molecule = database_service.get_single_molecule(molecule_id)

        # left side : display molecule data
        with col1:
            st.markdown(f'**Name** : {molecule.name}')
            st.markdown(f'**Formula** : {molecule.formula}')
            st.markdown(f'**Family** : {molecule.family}')

        # middle side : display molecule data
        with col2:
            st.markdown(f'**Link type** : {molecule.maximum_link}')
            st.markdown(f'**Atoms count** : {molecule.atoms_number}')
            st.markdown(f'**Links count** : {molecule.links_number}')

        # handler function
        def next_handler():
            st.session_state.selected_molecule_id = molecule_id

        # right side : display button
        with col3:
            st.button(key=100 + index, label='more details', on_click=next_handler)

    # get all molecules IDs
    @staticmethod
    def get_data():
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
        version_1, version_2, version_3, version_4 = Database().get_count_isomorphism_byVersion()
        print(f'\n\nVersion statistics : v1={version_1}, v2={version_2}, v3={version_3}, v4={version_4}')

        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        labels = 'Simple', 'Atom colored', 'Link colored', 'advanced'
        total = (version_1 + version_2 + version_3 + version_4) / 4
        st.markdown(f'**Total isomorphism : ** {int(total)}')
        if total != 0:
            sizes = [version_1, version_2, version_3, version_4]
            explode = (0.1, 0, 0, 0)

            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
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
        print(f'\n\nFamily statistics : {family_dict}')

        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        labels = list(family_dict.keys())
        total = sum(list(family_dict.values()))
        st.markdown('')
        if total != 0:
            sizes = list(family_dict.values())
            fig, ax = plt.subplots(figsize=(10, 5), subplot_kw=dict(aspect="equal"))

            data, auto_texts = ax.pie(sizes, textprops=dict(color="w"))
            ax.legend(data, labels,
                      title="Families",
                      loc="center left",
                      bbox_to_anchor=(1, 0, 0.5, 1))

            st.pyplot(fig)
