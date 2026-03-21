import sys
from kodys_lifecycle_api import *


def init():
    dropDatabase()
    migrate_app_database()
    # load_default_users()
    load_data(mode="BUILD")
    # load_default_account_users()


def load_data(mode="RUN", app_name=None):
    if mode.upper() == "RUN":
        run_fixtures(app_name)
    else:
        build_fixtures(app_name)
        run_fixtures(app_name)

if __name__ == '__main__':
    POSSIBLE_COMMANDS_LIST = ["init","loaddata"]
    if len(sys.argv) < 2:
        sys.exit("""Must provide args like \n\t %s"""%("\n\t ".join(POSSIBLE_COMMANDS_LIST)))
    else:
        if sys.argv[1] in POSSIBLE_COMMANDS_LIST:
            if sys.argv[1] == 'init':
                init()
            elif sys.argv[1] == 'loaddata':
                if len(sys.argv) == 3:
                    load_data(sys.argv[2])
                elif len(sys.argv) == 4:
                    load_data(sys.argv[2],sys.argv[3])
                else:
                    load_data()
            else:
                print("""Invalid argument, Must provide args like \n\t %s"""%("\n\t ".join(POSSIBLE_COMMANDS_LIST)))
            print("Done...")
        else:
            sys.exit("""Invalid argument, Must provide args like \n\t %s"""%("\n\t ".join(POSSIBLE_COMMANDS_LIST)))
