from dbconnection import DBConnection


class ConfigData:
    def __init__(self):
        pass

    def getClientData(self, client_id=0):
        connection = DBConnection().connect()
        result = connection.execute("select * from clients where id=?", (client_id, )).fetchone()
        connection.close()
        return result

    def getSettings(self):
        connection = DBConnection().connect()
        result = connection.execute("select setting_name, setting_value from freelancer_settings")
        # Add all settings into a dictionary and return
        settings = {}
        for row in result:
            settings[row['setting_name']] = row['setting_value']
        return settings
