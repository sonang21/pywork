import pymssql

vServerTarget = '100.100.100.164'
vUserTarget = 'ngadmin'
vPasswordTarget = '!Ad@NgTft#2017)'
vDatabaseTarget = 'ELOC2001'

conn1 = pymssql.connect(host=vServerTarget, user=vUserTarget, password=vPasswordTarget, database=vDatabaseTarget)

conn2 = pymssql.connect(host='localhost', user='sa', password='dba1020', database='DBMon')
cursor1 = conn1.cursor()
cursor2 = conn2.cursor()
sql1 = """
declare @sqlcmd nvarchar(max);

set @sqlcmd = '
if ''?'' not in (''tempdb'', ''msdb'') 
begin
use [?];

declare @logdate datetime = getdate();

set @logdate = getdate();
WITH V1 AS (
    SELECT S.OBJECT_ID
         , SUM(S.RESERVED_PAGE_COUNT)  AS RESERVED_PAGES
         , SUM(S.USED_PAGE_COUNT)      AS USED_PAGES
         , SUM(CASE WHEN S.INDEX_ID < 2 THEN (S.IN_ROW_DATA_PAGE_COUNT + S.LOB_USED_PAGE_COUNT + S.ROW_OVERFLOW_USED_PAGE_COUNT)
                    ELSE 0
               END) DATA_PAGES
         -- , SUM(S.RESERVED_PAGE_COUNT - S.USED_PAGE_COUNT) UNUSED_PAGES
         , SUM(CASE WHEN S.INDEX_ID < 2 THEN S.ROW_COUNT ELSE 0 END) NUM_ROWS
    FROM SYS.DM_DB_PARTITION_STATS S
    -- WHERE OBJECT_ID = OBJECT_ID(''''C_DCATE'''')
    GROUP BY S.OBJECT_ID
)
, V2 AS (
    SELECT T.PARENT_ID 
         , SUM(S.RESERVED_PAGE_COUNT) AS RESERVED_PAGES
         , SUM(S.USED_PAGE_COUNT)     AS USED_PAGES
    FROM SYS.DM_DB_PARTITION_STATS S
         INNER JOIN SYS.INTERNAL_TABLES T ON (T.OBJECT_ID = S.OBJECT_ID)
    GROUP BY T.PARENT_ID
)
SELECT DB_NAME()    AS DBNAME
     , S.NAME       AS SCHEMA_NAME
     , T.NAME       AS TABLE_NAME
     , @logdate     AS LOG_DT
     , P1.NUM_ROWS
     , ROUND( P1.DATA_PAGES * 8 / 1024.0, 2)                                      AS DATA_MB
     , ROUND((P1.USED_PAGES + ISNULL(P2.USED_PAGES, 0) - P1.DATA_PAGES) * 8 / 1024.0, 2) AS INDEX_MB 
     , ROUND((P1.USED_PAGES     + ISNULL(P2.USED_PAGES, 0))     * 8 / 1024.0, 2)  AS USED_MB 
     , ROUND((P1.RESERVED_PAGES + ISNULL(P2.RESERVED_PAGES,0) - P1.USED_PAGES - ISNULL(P2.USED_PAGES, 0)) * 8 / 1024.0, 2) UNUSED_MB 
     , ROUND((P1.RESERVED_PAGES + ISNULL(P2.RESERVED_PAGES,0))  * 8 / 1024.0, 2)  AS RESERVED_MB
FROM SYS.TABLES T 
     INNER JOIN SYS.SCHEMAS S   ON (S.SCHEMA_ID     = T.SCHEMA_ID)
     INNER JOIN V1          P1  ON (P1.OBJECT_ID    = T.OBJECT_ID)
     LEFT OUTER JOIN V2     P2  ON (P2.PARENT_ID    = T.OBJECT_ID)
ORDER BY S.NAME, T.NAME 
;
end
'
;

Exec sp_MSforeachdb @sqlcmd;

""" 

cursor1.execute(sql1)

sql2 = """
insert into dbo.DBM_TABSIZE (
      dbname        --nvarchar
    , schema_name   --nvarchar
    , table_name    --nvarchar
    , log_dt        --datetime
    , num_rows      --bigint
    , data_mb       --numeric
    , index_mb      --numeric
    , used_mb       --numeric
    , unused_mb     --numeric
    , reserved_mb   --numeric
) values (%s, %s, %s, %s, %d, %d, %d, %d, %d, %d)
"""

while cursor1:
    vRes1 = cursor1.fetchall()
    cursor2.executemany(sql2, vRes1)
    conn2.commit()

    if not cursor1.nextset():
        break
    pass

print("## END " + "#" * 80)
    
cursor1.close()
cursor2.close()
conn1.close()
conn2.close()
