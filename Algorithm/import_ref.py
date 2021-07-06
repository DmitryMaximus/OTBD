import jaydebeapi
import os
import datetime
import pandas as pd
from Config_read import confdict

database = confdict['SERVER_DATA']['database']
user = confdict['SERVER_DATA']['user']
password = confdict['SERVER_DATA']['password']
server = confdict['SERVER_DATA']['server']
sql_conn = jaydebeapi.connect("com.microsoft.sqlserver.jdbc.SQLServerDriver",
                                   f"""jdbc:sqlserver://{server}; databaseName={database}""",
                                   [user, password], confdict['SERVER_DATA']['path_to_manager'])