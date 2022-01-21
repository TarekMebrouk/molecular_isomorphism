from models.parser import *
from services.database import *

if __name__ == '__main__':
    # clear database rows
    database_service = Database()
    database_service.clear_tables()

    # run parsing method
    parser = Parser()
    parser.run()
