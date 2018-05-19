@echo off 

cd c:\2.MyDev\PyProjects\mssql
call c:\2.MyDev\PyProjects\mssql\myvenv\Scripts\activate 
python mssql_snap.py >> mssql_snap_log.txt 2>&1

exit

 

