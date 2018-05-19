from os import getenv
import pymssql
import sys
import datetime

# server = getenv("PYMSSQL_TEST_SERVER")
# user = getenv("PYMSSQL_TEST_USERNAME")
# password = getenv("PYMSSQL_TEST_PASSWORD")
#--------------------------------------------------------------------------------------------------
vIntervalMinutes = 20

vServerMon   = 'localhost'
vUserMon     = 'sa'
vPasswordMon = 'dba1020'
vDatabaseMon = 'DBMON'

vServerTarget = '100.100.100.164'
vUserTarget = 'ngadmin'
vPasswordTarget = '!Ad@NgTft#2017)'
vDatabaseTarget = 'ELOC2001'

#vServerTarget   = vServerMon
#vUserTarget     = vUserMon
#vPasswordTarget = vPasswordMon
#vDatabaseTarget = vDatabaseMon


#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

# conn = pymssql.connect(', user, password, "tempdb")
connMon = pymssql.connect(host=vServerMon, user=vUserMon, password=vPasswordMon, database=vDatabaseMon)
connTgt = pymssql.connect(host=vServerTarget, user=vUserTarget, password=vPasswordTarget, database=vDatabaseTarget)

cursorMon = connMon.cursor()
cursorTgt = connTgt.cursor()

cursorMon.execute("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED");
cursorTgt.execute("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED");


#--------------------------------------------------------------------------------------------------
#  001.DBM_SNAP
#--------------------------------------------------------------------------------------------------
vSnapId = 1
vLocalTime = datetime.datetime.now()

cursorTgt.execute("SELECT @@SERVERNAME AS SERVERNAME")
vRes1 = cursorTgt.fetchone()
vTargetServiceName = vRes1[0]

vSqlM = "select max(Snap_Id) + 1 as snap_id, getdate() snap_time from dbo.DBM_SNAP"
cursorMon.execute(vSqlM)
vRes1 = cursorMon.fetchone()

if not (vRes1 is None or vRes1[0] is None):
    vSnapId = vRes1[0]
    vSnapTime = vRes1[1]
else:
    vSnapId = 1
    vSnapTime = vRes1[1]

print("##[DB SERVER] %s" % vTargetServiceName)
print("##[001] DBM_SNAP : ", end='', flush=True)
print("Snap_id = %d, Snap_time = %s, local_time = %s" \
        % (vSnapId, vSnapTime.strftime('%Y-%m-%d %H:%M:%S.%f'), vLocalTime.strftime('%Y-%m-%d %H:%M:%S.%f')))
vSqlM = "insert into dbo.DBM_SNAP(snap_Id, snap_time, local_time) values(%d, convert(datetime, %s, 121), convert(datetime, %s, 121))"
cursorMon.execute(vSqlM, (vSnapId, vSnapTime.strftime('%Y-%m-%d %H:%M:%S'), vLocalTime.strftime('%Y-%m-%d %H:%M:%S')))
connMon.commit()

#--------------------------------------------------------------------------------------------------
#  002.DBM_STATS
#--------------------------------------------------------------------------------------------------
print("%-25s" % "##[002] DBM_STATS ", end='', flush=True)
vSqlT = """
select /* M002.03.DBM_STATS - WAITS */
       CAST(@@CPU_BUSY AS BIGINT)                                                                                                  as CPU_Busy
	 , CAST(@@CPU_BUSY AS BIGINT) + @@IO_BUSY + @@IDLE                                                                             as CPU_Total
	 , sum(convert(bigint, case when a.wait_type like 'LCK%'              then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Locks_ms
     , sum(convert(bigint, case when a.wait_type like 'LATCH%'            or
                                     a.wait_type like 'PAGELATCH%'        or
                                     a.wait_type like 'PAGEIOLATCH%'      then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Reads_ms
     , sum(convert(bigint, case when a.wait_type like '%IO_COMPLETION%'   or
                                     a.wait_type='WRITELOG'               then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Writes_ms
	 , sum(convert(bigint, case when a.wait_type in ('NETWORKIO','OLEDB') then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Networks_ms
	 , sum(convert(bigint, case when a.wait_type like 'BACKUP%' or
                                     a.wait_type='DISKIO_SUSPEND'         then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Backups_ms
	 , sum(convert(bigint, case when a.wait_type='PSS_CHILD'              then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Cursors_ms
	 , sum(convert(bigint, case when a.wait_type='ASYNC_DISKPOOL_LOCK'    or
                                     a.wait_type='ASYNC_IO_COMPLETION'    or
                                     a.wait_type='IO_COMPLETION'          or
                                     a.wait_type like 'PAGEIOLATCH%'      then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Disk_IO_ms
	 , sum(convert(bigint, case when a.wait_type='XACTLOCKINFO'           then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as LockInfo_ms
	 , sum(convert(bigint, case when a.wait_type='CMEMTHREAD'               or
                                     a.wait_type like 'RESOURCE_SEMAPHORE%' or
                                     a.wait_type='SOS_RESERVEDMEMBLOCKLIST'
                                                                          then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Memory_ms
     , sum(convert(bigint, case when a.wait_type like 'PAGELATCH%'        then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Latch_Page_ms
     , sum(convert(bigint, case when a.wait_type like 'PAGEIOLATCH%'      then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Latch_PageIo_ms
     , sum(convert(bigint, case when a.wait_type like 'PAGELATCH%'        or
                                     a.wait_type like 'PAGEIOLATCH%'      then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Latch_PageAll_ms
     , sum(convert(bigint, case when a.wait_type like 'LATCH%'            then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Latch_Others_ms
	 , sum(convert(bigint, case when a.wait_type like 'TRAN_MARKLATCH%'   then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Latch_Tran_ms
	 , sum(convert(bigint, case when a.wait_type='ASYNC_NETWORK_IO '      or
                                     a.wait_type like 'BROKER%'           or
                                     a.wait_type='CURSOR'                 or
                                     a.wait_type='CXPACKET'               or
                                     a.wait_type='EXCHANGE'               or
                                     a.wait_type='PAGESUPP'               or
                                     a.wait_type like 'PREEMPTIVE_%'      or
                                     a.wait_type like 'SLEEP%'            or
                                     a.wait_type='SOS_SCHEDULER_YIELD'    or
                                     a.wait_type='TEMPOBJ'                or
                                     a.wait_type='THREADPOOL'             or
                                     a.wait_type='XE_%'                   then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Others_ms
	 , sum(convert(bigint, case when a.wait_type='RESOURCE_QUERY_SEMAPHORE_COMPILE'
                                                                          then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as SqlCompile_ms
	 , sum(convert(bigint, case when a.wait_type='LOGBUFFER'              or
                                     a.wait_type='LOGMGR'                 or
                                     a.wait_type='WRITELOG'               then a.wait_time_ms - a.signal_wait_time_ms else 0 end)) as Tran_Log_ms
	 , @@TOTAL_READ  AS PhysicalReads_cnt
	 , @@TOTAL_WRITE AS PhysicalWrites_cnt
 from sys.dm_os_wait_stats a;
---------------+---------------+---------------+-----------------
select /* M001.01.DBM_STATS - IO, BatchRequests, SQLCompiles, Transactions */
       sum(case when a.counter_name = 'page lookups/sec'                      then a.cntr_value else 0 end)   LogcalReads
     , sum(case when a.object_name like   '%sql statistics%'
                     and a.counter_name = 'batch requests/sec'                then a.cntr_value else 0 end)   BatchRequests
     , sum(case when a.object_name like   '%sql statistics%'
                     and a.counter_name = 'sql compilations/sec'              then a.cntr_value else 0 end)   SQLCompiles
     , sum(case when a.object_name like   '%sql statistics%'
                     and a.counter_name = 'sql re-compilations/sec'           then a.cntr_value else 0 end)   SQLRecompiles
     , sum(case when a.object_name like   '%databases%'
                     and a.counter_name = 'transactions/sec'
                     and a.instance_name <> '_total'                          then a.cntr_value else 0 end)   Transactions
  from (select lower(a.counter_name)            counter_name
             , lower(a.object_name)             object_name
             , lower(a.instance_name)           instance_name
             , convert(bigint, a.cntr_value)    cntr_value 
         from  sys.dm_os_performance_counters a -- master..sysperfinfo a
       ) a ;
---------------+---------------+---------------+-----------------
select /* M001.02.DBM_STATS - CPU */
       top 1 convert(xml,record).value('(./Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]', 'int') CPU
  from sys.dm_os_ring_buffers
 where ((ring_buffer_type = 'RING_BUFFER_SCHEDULER_MONITOR') and (record like '%<SystemHealth>%'))
 order by timestamp desc;

"""
cursorTgt.execute(vSqlT)
print("...", end="", flush=True)

vRes1 = [ row for row in cursorTgt ]
vRes2 = [ row for row in cursorTgt ]
vRes3 = [ row for row in cursorTgt ]

vNowTime = datetime.datetime.now()
print("[%s, " % (vNowTime-vLocalTime), end="", flush=True)

vSqlM = """
insert into dbo.DBM_STATS (
    Snap_Id
  -------------------S1
  , CPU_Busy
  , CPU_Total
  , Locks_ms
  , Reads_ms
  , Writes_ms
  ---------------+
  , Networks_ms
  , Backups_ms
  , Cursors_ms
  , DISK_IO_ms
  , LockInfo_ms
  ---------------+
  , Memory_ms
  , Latch_Page_ms
  , Latch_PageIo_ms
  , Latch_PageAll_ms
  , Latch_Others_ms
  ---------------+
  , Latch_Tran_ms
  , Others_ms
  , SqlCompile_ms
  , Tran_Log_ms
  , PhysicalReads_cnt
  ---------------+
  , PhysicalWrites_cnt
  -------------------S2
  , LogicalReads_cnt
  , BatchRequest_cnt
  , SqlCompile_cnt
  , SqlRecompile_cnt
  , Transaction_cnt
  -------------------S3
  , CPU
  ---------------+
)
values( %d, %d, %d, %d, %d, %d, %d, %d, %d, %d
      , %d, %d, %d, %d, %d, %d, %d, %d, %d, %d
      , %d, %d, %d, %d, %d, %d, %d, %d)
"""

vDataSet = [vSnapId] + list(vRes1[0]) + list(vRes2[0]) + list(vRes3[0])
vDataSet = tuple(vDataSet)
cursorMon.execute(vSqlM, vDataSet)
connMon.commit()

vNowTime = datetime.datetime.now()
print ("%s]... OK(%d)" % (vNowTime-vLocalTime, len(vRes1)))


#--------------------------------------------------------------------------------------------------
#  DBM_OS_WAITS
#--------------------------------------------------------------------------------------------------
print("%-25s" % "##[003] DBM_OS_WAITS", end="", flush=True)
vSqlT = """
 select %d   snap_id
      , a.wait_type
      , a.waiting_tasks_count
      , a.wait_time_ms
      , a.max_wait_time_ms
      , a.signal_wait_time_ms
 from sys.dm_os_wait_stats a
"""
cursorTgt.execute(vSqlT, vSnapId)
print("...", end="", flush=True)
vRes1 = cursorTgt.fetchall()

vNowTime = datetime.datetime.now()
print("[%s, " % (vNowTime-vLocalTime), end="", flush=True)

vSqlM = """
  insert into dbo.DBM_OS_WAITS
  (  snap_id
   , wait_type
   , waiting_tasks_count
   , wait_time_ms
   , max_wait_time_ms
   , signal_wait_time_ms
  )
  values (%d, %s, %d, %d, %d, %d)
"""

cursorMon.executemany(vSqlM, vRes1)
connMon.commit()

vNowTime = datetime.datetime.now()
print ("%s]... OK(%d)" % (vNowTime-vLocalTime, len(vRes1)))

#--------------------------------------------------------------------------------------------------
#  DBM_PERF_CNTR
#--------------------------------------------------------------------------------------------------
print("%-25s" % "##[004] DBM_PERF_CNTR", end="", flush=True)
vSqlT = """
 select /* M003.01 DBM_PERF_CNTR (sysperfinfo) */
        %d   snap_id
      , a.object_name
      , a.counter_name
	  , a.instance_name
	  , a.cntr_value
	  , a.cntr_type
 from sys.dm_os_performance_counters a
"""
cursorTgt.execute(vSqlT, vSnapId)
print("...", end="", flush=True)
vRes1 = cursorTgt.fetchall()

vNowTime = datetime.datetime.now()
print("[%s, " % (vNowTime-vLocalTime), end="", flush=True)

vSqlM = """
  insert into dbo.DBM_PERF_CNTR (Snap_id, object_name, counter_name, instance_name, cntr_value, cntr_type)
  values (%d, %s, %s, %s, %d, %d)
"""
cursorMon.executemany(vSqlM, vRes1)
connMon.commit()

vNowTime = datetime.datetime.now()
print ("%s]... OK(%d)" % (vNowTime-vLocalTime, len(vRes1)))

#--------------------------------------------------------------------------------------------------
#  DBM_SESSIONS
#--------------------------------------------------------------------------------------------------
print("%-25s" % "##[005] DBM_SESSIONS", end="", flush=True)
vSqlT = """
select /* M004.01 DBM_SESSIONS(active session info) */
       %d  snap_id
     , a.session_id
     , a.login_time
     , a.last_request_start_time
     , a.last_request_end_time
     , a.host_name
     , a.login_name
     , a.program_name
     , a.client_interface_name
     , a.status
     , a.total_elapsed_time
     , a.reads
     , a.writes
     , a.logical_reads
     , a.row_count
     , a.open_transaction_count
 from sys.dm_exec_sessions a with(readuncommitted)
--  where (   a.last_request_start_time >= dateadd(minute, -%d, getdate())
--         or a.last_request_end_time   >= dateadd(minute, -%d, getdate())
--        )
"""
cursorTgt.execute(vSqlT, (vSnapId, vIntervalMinutes+3, vIntervalMinutes+3))
print("...", end="", flush=True)
vRes1 = cursorTgt.fetchall()

vNowTime = datetime.datetime.now()
print("[%s, " % (vNowTime-vLocalTime), end="", flush=True)

vSqlM = """
insert into dbo.DBM_SESSIONS(
	  Snap_Id                     -- bigint      NOT NULL
	, session_id                  -- smallint
	, login_time                  -- datetime
	, last_request_start_time     -- datetime
	, last_request_end_time       -- datetime
	-------------------------------- 
	, host_name                   -- nvarchar(256)
    , login_name                  -- nvarchar(256)
    , program_name                -- nvarchar(256)
    , client_interface_name       -- nvarchar(64)
    , status                      -- nvarchar(60)
    -------------------------------- 
	, total_elapsed_time          -- bigint
    , reads                       -- bigint
    , writes                      -- bigint
    , logical_reads               -- bigint
    , row_count                   -- bigint
    -------------------------------- 
	, open_transaction_count      -- int
)
values( %d, %d, %s, %s, %s   , %s, %s, %s, %s, %s   , %d, %d, %d, %d, %d   , %d)
"""
cursorMon.executemany(vSqlM, vRes1)
connMon.commit();

vNowTime = datetime.datetime.now()
print ("%s]... OK(%d)" % (vNowTime-vLocalTime, len(vRes1)))

#--------------------------------------------------------------------------------------------------
#  DBM_REQUESTS
#--------------------------------------------------------------------------------------------------
print("%-25s" % "##[006] DBM_REQUESTS", end="", flush=True)

vSqlT = """
select /* M005.01 DBM_REQUESTS (active sql info) */
       %d  snap_id
     , a.session_id
     , a.request_id
	 , a.start_time
	 , a.total_elapsed_time
	 , a.status
	 , a.command
	 , a.sql_handle
	 , a.statement_start_offset
	 , a.statement_end_offset
	 , a.statement_sql_handle
	 , a.blocking_session_id
	 , a.wait_type
	 , a.wait_time
	 , a.last_wait_type
	 , a.wait_resource
	 , a.percent_complete
	 , a.estimated_completion_time
	 , a.cpu_time
	 , a.logical_reads
  from sys.dm_exec_requests a
-- where (a.status = 'running'
--        or a.start_time >= dateadd(minute, -%d, getdate())
--       )
;
"""
cursorTgt.execute(vSqlT, (vSnapId, vIntervalMinutes+3))
print("...", end="", flush=True)
vRes1 = cursorTgt.fetchall()

vNowTime = datetime.datetime.now()
print("[%s, " % (vNowTime-vLocalTime), end="", flush=True)

vSqlM = """
insert into dbo.DBM_REQUESTS(
        Snap_Id
      , session_id
      , request_id
      , start_time
      , total_elapsed_time
      ----------------------------
      , status
      , command
      , sql_handle
      , statement_start_offset
      , statement_end_offset
      ----------------------------
      , statement_sql_handle
      , blocking_session_id
      , wait_type
      , wait_time
      , last_wait_type
      ----------------------------
      , wait_resource
      , percent_complete
      , estimated_completion_time
      , cpu_time
      , logical_reads
) values ( %d, %d, %d, convert(datetime, %s, 121), %d
         , %s, %s, convert(varbinary, %s), %d, %d
         , convert(varbinary, %s), %d, %s, %d, %s
         , %s, %d, %d, %d, %d)
"""
cursorMon.executemany(vSqlM, vRes1)
connMon.commit()

vNowTime = datetime.datetime.now()
print ("%s]... OK(%d)" % (vNowTime-vLocalTime, len(vRes1)))

#--------------------------------------------------------------------------------------------------
#  DBM_SQLSTATS
#--------------------------------------------------------------------------------------------------
print("%-25s" % "##[007] DBM_SQLSTATS", end="", flush=True)

vSqlT = """
select /* M006.01 DBM_SQLSTATS (dm_exec_query_stats) */
       %d  snap_id
     , a.sql_handle
     , a.statement_start_offset
	 , a.statement_end_offset
	 , a.plan_generation_num
	 , a.plan_handle
	 , a.creation_time
	 , a.last_execution_time
	 , a.execution_count
	 , a.total_worker_time
	 , a.max_worker_time
	 , a.total_physical_reads
	 , a.max_physical_reads
	 , a.total_logical_writes
	 , a.max_logical_writes
	 , a.total_logical_reads
	 , a.max_logical_reads
	 , a.total_clr_time
	 , a.max_clr_time
	 , a.total_elapsed_time
	 , a.max_elapsed_time
	 , a.total_rows
	 , a.max_rows
  from sys.dm_exec_query_stats a
 where a.last_execution_time >= dateadd(minute, -%d, getdate())
;
"""
cursorTgt.execute(vSqlT, (vSnapId, vIntervalMinutes + 3))
print("...", end="", flush=True)
vRes1 = cursorTgt.fetchall()

vNowTime = datetime.datetime.now()
print("[%s, " % (vNowTime-vLocalTime), end="", flush=True)

vSqlM = """
insert into dbo.DBM_SQLSTATS(
	  Snap_Id                     -- bigint
    , sql_handle                  -- varbinary(64)
    , statement_start_offset      -- int
    , statement_end_offset        -- int
    , plan_generation_num         -- bigint
    --------------------------------
	, plan_handle                 -- varbinary(64)
    , creation_time               -- datetime
    , last_execution_time         -- datetime
    , execution_count             -- bigint
    , total_worker_time           -- bigint
    --------------------------------
	, max_worker_time             -- bigint
    , total_physical_reads        -- bigint
    , max_physical_reads          -- bigint
    , total_logical_writes        -- bigint
    , max_logical_writes          -- bigint
    --------------------------------
	, total_logical_reads         -- bigint
    , max_logical_reads           -- bigint
    , total_clr_time              -- bigint
    , max_clr_time                -- bigint
    , total_elapsed_time          -- bigint
    --------------------------------
	, max_elapsed_time            -- bigint
    , total_rows                  -- bigint
    , max_rows                    -- bigint
) values (  %d, convert(varbinary,%s), %d, %d, %d
          , convert(varbinary, %s), %s, %s, %d, %d
          , %d, %d, %d, %d, %d
          , %d, %d, %d, %d, %d
          , %d, %d, %d
         )
"""
cursorMon.executemany(vSqlM, vRes1)
connMon.commit()

vNowTime = datetime.datetime.now()
print ("%s]... OK(%d)" % (vNowTime-vLocalTime, len(vRes1)))

#--------------------------------------------------------------------------------------------------
#  DBM_SQLTEXT
#--------------------------------------------------------------------------------------------------
print("%-25s" % "##[008] DBM_SQLTEXT", end="", flush=True)

vSqlT = """
select a.sql_handle                         sql_handle_for_check 
     , a.sql_handle                         sql_handle
     , db_name(b.dbid)                      dbname
     , object_name(b.objectid, b.dbid)      objectname 
     , b.text
     , getdate()                            log_dt
from (select distinct sql_handle 
        from sys.dm_exec_query_stats 
	   where creation_time > dateadd(minute, -%d, getdate())
	 ) a 
     cross apply sys.dm_exec_sql_text(a.sql_handle) b 
where b.text not like 'FETCH API_CURSOR%'
;
"""
cursorTgt.execute(vSqlT, vIntervalMinutes + 3)
print("...", end="", flush=True)
vRes1 = cursorTgt.fetchall()

vNowTime = datetime.datetime.now()
print("[%s, " % (vNowTime-vLocalTime), end="", flush=True)

vSqlM = """
if not exists(select 1 from dbo.DBM_SQLTEXT where sql_handle = convert(varbinary, %s))
insert into dbo.DBM_SQLTEXT (
	  sql_handle  -- varbinary(64)
    , dbname      -- nvarchar(256)
    , objectname  -- nvarchar(256)
    , text        -- nvarchar(max)
    , log_dt      -- datetime
	--------------------------------------------
)
values ( convert(varbinary, %s), %s, %s, %s, %s
       )
"""
# print(vRes1)
cursorMon.executemany(vSqlM, vRes1)

################################################################################
# for debugging
#for ix in range(len(vRes1)):
#    print("."*10 + "%d" % ix)
#    
#    try:
#        cursorMon.execute(vSqlM, vRes1[ix])
#    except Exception as e:
#        print(e)
#        print("=" * 80)
#        print(vRes1[ix])
#        nx=0
#        for data in (vRes1[ix]):
#            nx += 1
#            print("[%d] : "  % (nx), end='')
#            print("%s" % str(data))
#            
#        break
################################################################################

connMon.commit()

vNowTime = datetime.datetime.now()
print ("%s]... OK(%d)" % (vNowTime-vLocalTime, len(vRes1)))

#--------------------------------------------------------------------------------------------------
#  DBM_TABSIZE
#--------------------------------------------------------------------------------------------------
print("%-25s" % "##[009] DBM_TABSIZE", end="", flush=True)

vSqlT = """
declare @sqlcmd nvarchar(max);

set @sqlcmd = '
if ''?'' not in (''tempdb'', ''msdb'') 
begin
use [?];

declare @logdate datetime = getdate();
declare @snap_id bigint = %d;

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
SELECT @snap_id     as snap_id
     , DB_NAME()    AS DBNAME
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
';

Exec sp_MSforeachdb @sqlcmd;
"""
cursorTgt.execute(vSqlT, (vSnapId))
print("...", end="", flush=True)

vSqlM = """
insert into dbo.DBM_TABSIZE (
      Snap_id       --bigint 
    , dbname        --nvarchar
    , schema_name   --nvarchar
    , table_name    --nvarchar
    , log_dt        --datetime
    , num_rows      --bigint
    , data_mb       --numeric
    , index_mb      --numeric
    , used_mb       --numeric
    , unused_mb     --numeric
    , reserved_mb   --numeric
) values (%d, %s, %s, %s, %s, %d, %d, %d, %d, %d, %d)
"""

vRowCount = 0
while cursorTgt:
    vRes1 = cursorTgt.fetchall()
    vRowCount += len(vRes1)
    cursorMon.executemany(vSqlM, vRes1)
    connMon.commit()

    if not cursorTgt.nextset():
        break
    pass

vNowTime = datetime.datetime.now()
print("[%s, " % (vNowTime-vLocalTime), end="", flush=True)

vNowTime = datetime.datetime.now()
print ("%s]... OK(%d)" % (vNowTime-vLocalTime, vRowCount))


#--------------------------------------------------------------------------------------------------
#  DBM_ACTIONS
#--------------------------------------------------------------------------------------------------
print("%-25s" % "##[010] DBM_ACTIONS", end="", flush=True)

vSqlT = """
select
       a.session_id                                                     as session_id
     , a.blocking_session_id                                            as block_spid
     , case when a.statement_end_offset = -1 then d.text 
            else substring(
                     d.text
                   , a.statement_start_offset / 2 + 1
                   , (a.statement_end_offset - statement_start_offset) / 2 + 1
			     )
       end                                                              as query_text
     , b.program_name
     , b.host_name
     , c.client_net_address
     , right('0' + cast(a.total_elapsed_time/1000/60/60              as varchar), 2)
       + ':' + right('0' + cast((a.total_elapsed_time/1000/60) % 60  as varchar), 2)
       + ':' + right('0' + cast((a.total_elapsed_time/1000)    % 60  as varchar), 2) as elapsed_hms
     , a.total_elapsed_time
     , a.cpu_time
     , a.logical_reads
     , a.reads                                                          as physical_reads
     , a.writes
     , d.text                                                           as sql_full_text
     , a.status
     , a.wait_type
     , a.start_time
     , a.plan_handle
     , getdate()                                                        as log_dt
  from sys.dm_exec_requests                 a
       inner join sys.dm_exec_sessions      b on (a.session_id = b.session_id)
       inner join sys.dm_exec_connections   c on (a.session_id = c.session_id)
       cross apply sys.dm_exec_sql_text(a.sql_handle) as d
 where a.session_id > 50
   and d.text not like 'FETCH_API%'
"""
cursorTgt.execute(vSqlT)
print("...", end="", flush=True)

vSqlM = """
insert into dbo.DBM_ACTIONS (
	  Snap_Id                -- bigint      NOT NULL
    , session_id             -- smallint
    , block_spid             -- smallint
    , query_text             -- nvarchar(max)
    , program_name           -- nvarchar(256)
    -----------------------------------------------
    , host_name              -- nvarchar(256)
    , client_net_address     -- varchar(48)
    , elapsed_time_hms       -- varchar(14)
    , total_elapsed_time     -- int
    , cpu_time               -- int
    -----------------------------------------------
    , logical_reads          -- bigint
    , reads                  -- bigint
    , writes                 -- bigint
    , text                   -- nvarchar(max)
    , status                 -- nvarchar(60)
    -----------------------------------------------
    , wait_type              -- nvarchar(120)
    , start_time             -- datetime 
    , plan_handle            -- varbinary(64)
    , log_dt                 -- datetime
) values (%d, %d, %d, %s, %s
        , %s, %s, %s, %d, %d
        , %d, %d, %d, %s, %s
        , %s, %s, convert(varbinary(64),%s), %s
         )
"""

vRowCount = 0
del vRes1[:]
vOneRow = cursorTgt.fetchone()
while vOneRow:
    vRes1.append((vSnapId,) + vOneRow)
    vOneRow = cursorTgt.fetchone()

vNowTime = datetime.datetime.now()
print("[%s, " % (vNowTime-vLocalTime), end="", flush=True)

vRowCount = len(vRes1)
try:
    cursorMon.executemany(vSqlM, vRes1)
    connMon.commit()
except Exception as e:
    print(e)
    print("e" * 80)
    print(vRes1)
    
vNowTime = datetime.datetime.now()
print ("%s]... OK(%d)" % (vNowTime-vLocalTime, len(vRes1)))


#--------------------------------------------------------------------------------------------------
#  Ending
#--------------------------------------------------------------------------------------------------
cursorTgt.close()
connTgt.close()

cursorMon.close()
connMon.close()

print ('## END: snap_id = %d, snap_time = %s, end_local_time = %s' % (vSnapId \
                                                        , vSnapTime.strftime('%Y-%m-%d %H:%M:%S.%f') \
                                                        , datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
print ('*' * 80)
