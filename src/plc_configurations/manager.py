import os
import json
import configparser


class Manager:
    __languages = None

    @staticmethod
    def getLanguages():
        languagesConfigsPath = os.getcwd() + '/plc_configurations/languages.json'

        # Read only once, simulate Swift 'lazy' behaviour.
        if Manager.__languages is None:
            with open(languagesConfigsPath) as jsonFile:
                Manager.__languages = json.load(jsonFile)

        return Manager.__languages


# if __name__ == '__main__':
#     Manager.config()['DEFAULT']['MYSQL_PORT']
#     # or, better:
#     Manager.config().get(section='DEFAULT', option='MYSQL_PORT', fallback=3306)