import json


# 'SettingsManager' class declaration and definition
class SettingsManager:
    @staticmethod
    def getUserPreferences():
        with open("../data/userPreferences.json", mode="r") as inputFile:
            return json.load(inputFile)

    @staticmethod
    def setUserPreferences(prefChanges: dict):
        userPrefs = SettingsManager.getUserPreferences()

        # Change only the specified setting
        userPrefs.update(prefChanges)

        with open("../data/userPreferences.json", mode="w") as outputFile:
            json.dump(userPrefs, outputFile, indent=4)
