from os import getenv
import pymssql

server = getenv("PYMSSQL_TEST_SERVER")
user = getenv("PYMSSQL_TEST_USERNAME")
password = getenv("PYMSSQL_TEST_PASSWORD")

# conn = pymssql.connect(', user, password, "tempdb")
conn = pymssql.connect(host='localhost', user='sa', password='dba1020', database='tempdb')

cursor = conn.cursor()
cursor.execute("""
IF OBJECT_ID('persons', 'U') IS NOT NULL
    DROP TABLE persons
CREATE TABLE persons (
    id INT NOT NULL,
    name VARCHAR(100),
    salesrep VARCHAR(100),
    PRIMARY KEY(id)
)
""")

print ("""
--------------------------------------------------------------------
insert into person : executemany with array
--------------------------------------------------------------------
""")


cursor.executemany(
    "INSERT INTO persons VALUES (%d, %s, %s)",
    [(1, 'John Smith', 'John Doe'),
     (2, 'Jane Doe', 'Joe Dog'),
     (3, 'Mike T.', 'Sarah H.')])

# you must call commit() to persist your data if you don't set autocommit to True
conn.commit()

# cursor.execute('SELECT * FROM persons WHERE salesrep=%s', 'John Doe')
# print ('select from person')
cursor.execute('SELECT * FROM persons')
row = cursor.fetchone()
while row:
    print("ID=%d, Name=%s" % (row[0], row[1]))
    row = cursor.fetchone()

    
print ("""
--------------------------------------------------------------------
insert many with data dictionaries
--------------------------------------------------------------------
""")
data_dic = []
data_dic.append ((10, 'J.H.Song', 'Junghoon Song'))
data_dic.append ((11, 'sonang', 'sonang21@admin.com'))
data_dic.append ((12, 'tester', 'tester.com'))

sql_cmd = "insert into persons values (%d, %s, %s)"
cursor.executemany(sql_cmd, data_dic)
conn.commit

cursor.execute('SELECT * FROM persons')
results = cursor.fetchall()
for row in results:
  print (row)
   
    

conn.close()