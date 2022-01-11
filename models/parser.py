
class Parser:

    def __init__(self):
        # initialize molecules file path
        self.source_path = '../ChEBI_complete_3star.sdf'

        # initialize molecules IDs
        self.molecules_ID = []
        self.debug_level = 0

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
