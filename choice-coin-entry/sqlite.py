import sqlite3 as sl

conn = sl.connect("voters.db")
# with conn:
#     conn.execute(
#         """CREATE TABLE USER (
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#             DL VARCHAR(300),
#             SS VARCHAR(300)""")
