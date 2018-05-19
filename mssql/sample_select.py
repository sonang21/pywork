import pymssql
conn = pymssql.connect(host='localhost', user='sa', password='dba1020', database='DBMon')
cursor = conn.cursor()
sql = "SELECT  SERVERPROPERTY('MachineName') AS [ServerName], \
        SERVERPROPERTY('ServerName') AS [ServerInstanceName], \
        SERVERPROPERTY('InstanceName') AS [Instance], \
        SERVERPROPERTY('Edition') AS [Edition], \
        SERVERPROPERTY('ProductVersion') AS [ProductVersion], \
        Left(@@Version, Charindex('-', @@version) - 2) As VersionName" 
cursor.execute(sql)
results = cursor.fetchall()
for row in results:
  print (row)
