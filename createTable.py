import sqlite3

con = sqlite3.connect('environment.db')
cur = con.cursor()

cur.execute('''CREATE TABLE environment
               (time INTEGER, id TEXT, temperature REAL, humidity INT, pressure REAL, eco2 INT, tvoc INT, battery INT)''')

con.commit()

con.close()