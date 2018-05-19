SET ThousandSep=',';
SET DecimalSep='.';
SET MoneyThousandSep=',';
SET MoneyDecimalSep='.';
SET MoneyFormat='₩#,##0;-₩#,##0';
SET TimeFormat='TT h:mm:ss';
SET DateFormat='YYYY-MM-DD';
SET TimestampFormat='YYYY-MM-DD TT h:mm:ss[.fff]';
SET FirstWeekDay=6;
SET BrokenWeeks=1;
SET ReferenceDay=0;
SET FirstMonthOfYear=1;
SET CollationLocale='ko-KR';
SET MonthNames='1;2;3;4;5;6;7;8;9;10;11;12';
SET LongMonthNames='1월;2월;3월;4월;5월;6월;7월;8월;9월;10월;11월;12월';
SET DayNames='월;화;수;목;금;토;일';
SET LongDayNames='월요일;화요일;수요일;목요일;금요일;토요일;일요일';

OLEDB CONNECT32 TO [Provider=SQLOLEDB.1;Persist Security Info=True;User ID=sa;Initial Catalog=DBMon;Data Source=10.10.110.19;Use Procedure for Prepare=1;Auto Translate=True;Packet Size=4096;Workstation ID=LG-NOTE360;Use Encryption for Data=False;Tag with column collation when possible=False] (XPassword is KZUABSJMBLMADZAGXD);



//-------- Start Multiple Select Statements ------

//set vDateStart = "2017-11-02";
//set vDateEnd = "2017-11-02";
let vDateStart = Date(vDateStart, "YYYY-MM-DD");
let vDateEnd = Date(vDateEnd, "YYYY-MM-DD");

TRACE $(vDateStart);
TRACE $(vDateEnd);

//DISP_ITEM:
//load * inline [
//ITEM
//CPU
//Locks
//Reads
//];

PRE_EXEC:
SQL SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Get Min & Max Snap_id during period
SQLSnapID:
    LOAD SNAP_ID_START, SNAP_ID_END;
    SELECT min(snap_id) as SNAP_ID_START
         , max(snap_id) as SNAP_ID_END
    FROM dbo.DBM_SNAP 
	WHERE snap_time between convert(datetime, '$(vDateStart)', 120) and dateadd(DD, 1, convert(datetime, '$(vDateEnd)', 120))
	;
    // WHERE BEGIN_INTERVAL_TIME >=  --SYSDATE - $(vDayBefore);

let vSnapIDStart = Peek('SNAP_ID_START',0,'SQLSnapID');
let vSnapIDEnd   = Peek('SNAP_ID_END'  ,0,'SQLSnapID');


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Retrieve snap information
DBM_SNAP:
SQL select a.snap_id, substring(convert(varchar, a.snap_time, 120), 9, 8) snap_time 
         , datediff(second, lag(a.snap_time) over (order by a.snap_id), a.snap_time) snap_interval_sec
    from dbo.DBM_SNAP a
    where a.snap_id between $(vSnapIDStart) and $(vSnapIDEnd)
	order by a.snap_id;

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// dm_os_wait_stats, dm_os_performance_counters
DBM_STATS:
SQL with V_DBM_STATS as (
	    select a.snap_id
	         , a.CPU
	         , a.Locks_ms
	         , a.Reads_ms
	         , a.Writes_ms
	         , a.Networks_ms
	         , a.DISK_IO_ms
	         , a.Latch_Page_ms
	         , a.Latch_PageIo_ms
			 , a.SqlCompile_ms
	         , a.Tran_Log_ms
	         , a.PhysicalReads_cnt
	         , a.PhysicalWrites_cnt
	         , a.LogicalReads_cnt
	         , a.BatchRequest_cnt
	         , a.SqlCompile_cnt
	         , a.SqlRecompile_cnt
	         , a.Transaction_cnt
             --------------------------------------------------------------------
             , lag(a.Locks_ms            ) over (order by a.snap_id) Locks_ms2
             , lag(a.Reads_ms            ) over (order by a.snap_id) Reads_ms2
             , lag(a.Writes_ms           ) over (order by a.snap_id) Writes_ms2
             , lag(a.Networks_ms         ) over (order by a.snap_id) Networks_ms2
             , lag(a.DISK_IO_ms          ) over (order by a.snap_id) DISK_IO_ms2            ------5
             , lag(a.Latch_Page_ms       ) over (order by a.snap_id) Latch_Page_ms2
             , lag(a.Latch_PageIo_ms     ) over (order by a.snap_id) Latch_PageIo_ms2
             , lag(a.SqlCompile_ms       ) over (order by a.snap_id) SqlCompile_ms2
             , lag(a.Tran_Log_ms         ) over (order by a.snap_id) Tran_Log_ms2
             , lag(a.PhysicalReads_cnt   ) over (order by a.snap_id) PhysicalReads_cnt2     ------10
             , lag(a.PhysicalWrites_cnt  ) over (order by a.snap_id) PhysicalWrites_cnt2
             , lag(a.LogicalReads_cnt    ) over (order by a.snap_id) LogicalReads_cnt2
             , lag(a.BatchRequest_cnt    ) over (order by a.snap_id) BatchRequest_cnt2
             , lag(a.SqlCompile_cnt      ) over (order by a.snap_id) SqlCompile_cnt2
             , lag(a.SqlRecompile_cnt    ) over (order by a.snap_id) SqlRecompile_cnt2      ------15
             , lag(a.Transaction_cnt     ) over (order by a.snap_id) Transaction_cnt2
             -------------------------------------------------------------------
             , datediff(second, lag(b.snap_time) over (order by a.snap_id), b.snap_time)  as interval_sec
	    from dbo.DBM_STATS a
             JOIN dbo.DBM_SNAP b on (b.snap_id = a.snap_id)
	    where a.snap_id between $(vSnapIDStart)-1 and $(vSnapIDEnd)
	)
	select a.snap_id
	     , a.CPU
	     , (case when a.Locks_ms           >= a.Locks_ms2            then (a.Locks_ms           - a.Locks_ms2            ) else a.Locks_ms           end) / a.interval_sec as  Locks_ms
	     , (case when a.Reads_ms           >= a.Reads_ms2            then (a.Reads_ms           - a.Reads_ms2            ) else a.Reads_ms           end) / a.interval_sec as  Reads_ms
	     , (case when a.Writes_ms          >= a.Writes_ms2           then (a.Writes_ms          - a.Writes_ms2           ) else a.Writes_ms          end) / a.interval_sec as  Writes_ms
	     , (case when a.Networks_ms        >= a.Networks_ms2         then (a.Networks_ms        - a.Networks_ms2         ) else a.Networks_ms        end) / a.interval_sec as  Networks_ms
	     , (case when a.DISK_IO_ms         >= a.DISK_IO_ms2          then (a.DISK_IO_ms         - a.DISK_IO_ms2          ) else a.DISK_IO_ms         end) / a.interval_sec as  DISK_IO_ms
	     , (case when a.Latch_Page_ms      >= a.Latch_Page_ms2       then (a.Latch_Page_ms      - a.Latch_Page_ms2       ) else a.Latch_Page_ms      end) / a.interval_sec as  Latch_Page_ms
	     , (case when a.Latch_PageIo_ms    >= a.Latch_PageIo_ms2     then (a.Latch_PageIo_ms    - a.Latch_PageIo_ms2     ) else a.Latch_PageIo_ms    end) / a.interval_sec as  Latch_PageIo_ms
	     , (case when a.SqlCompile_ms      >= a.SqlCompile_ms2       then (a.SqlCompile_ms      - a.SqlCompile_ms2       ) else a.SqlCompile_ms      end) / a.interval_sec as  SqlCompile_ms
	     , (case when a.Tran_Log_ms        >= a.Tran_Log_ms2         then (a.Tran_Log_ms        - a.Tran_Log_ms2         ) else a.Tran_Log_ms        end) / a.interval_sec as  Tran_Log_ms
	     , (case when a.PhysicalReads_cnt  >= a.PhysicalReads_cnt2   then (a.PhysicalReads_cnt  - a.PhysicalReads_cnt2   ) else a.PhysicalReads_cnt  end) / a.interval_sec as  PhysicalReads_cnt
	     , (case when a.PhysicalWrites_cnt >= a.PhysicalWrites_cnt2  then (a.PhysicalWrites_cnt - a.PhysicalWrites_cnt2  ) else a.PhysicalWrites_cnt end) / a.interval_sec as  PhysicalWrites_cnt
	     , (case when a.LogicalReads_cnt   >= a.LogicalReads_cnt2    then (a.LogicalReads_cnt   - a.LogicalReads_cnt2    ) else a.LogicalReads_cnt   end) / a.interval_sec as  LogicalReads_cnt
	     , (case when a.BatchRequest_cnt   >= a.BatchRequest_cnt2    then (a.BatchRequest_cnt   - a.BatchRequest_cnt2    ) else a.BatchRequest_cnt   end) / a.interval_sec as  BatchRequest_cnt
	     , (case when a.SqlCompile_cnt     >= a.SqlCompile_cnt2      then (a.SqlCompile_cnt     - a.SqlCompile_cnt2      ) else a.SqlCompile_cnt     end) / a.interval_sec as  SqlCompile_cnt
	     , (case when a.SqlRecompile_cnt   >= a.SqlRecompile_cnt2    then (a.SqlRecompile_cnt   - a.SqlRecompile_cnt2    ) else a.SqlRecompile_cnt   end) / a.interval_sec as  SqlRecompile_cnt
	     , (case when a.Transaction_cnt    >= a.Transaction_cnt2     then (a.Transaction_cnt    - a.Transaction_cnt2     ) else a.Transaction_cnt    end) / a.interval_sec as  Transaction_cnt
    from   V_DBM_STATS a
    where  a.snap_id >= $(vSnapIDStart)
	order by a.snap_id
;

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// DBM_STATS Column List
FOR i = 1 to NoOfFields('DBM_STATS')
DBM_STATS_COLUMNS:
LOAD $(i) as RowNum
     , FieldName($(i), 'DBM_STATS') as ITEM
Autogenerate(1);
NEXT i;


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CPU counter from dm_os_performance_counters
DBM_CPU:
SQL select a.snap_id, object_name
	     , sum(case when counter_name = 'CPU usage %' then cntr_value else 0.0 end)
		   / sum(case when counter_name = 'CPU usage % base' then cntr_value else 0.0 end) CPU_Usage
		 , instance_name 
	from dbo.DBM_PERF_CNTR a 
	where a.counter_name like 'CPU usage %'
	  and a.object_name like '%Resource Pool Stats%'
	  and a.snap_id between $(vSnapIDStart) and $(vSnapIDEnd)
	group by a.snap_id, a.object_name, a.instance_name 
	order by 1 desc, 2, 3
;

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// OS Waits from dm_os_wait_stats
DBM_OS_WAITS:
SQL select a.snap_id, a.wait_type
         , a.waiting_task_count
         , a.wait_time_ms
         , a.waiting_task_count / interval_minute   waiting_task_count_permin
         , a.wait_time_ms       / interval_minute   waiting_time_ms_permin
         , a.interval_minute
    from (
        select a.snap_id, a.wait_type
             , a.waiting_tasks_count - lag(a.waiting_tasks_count) over (partition by a.wait_type order by a.snap_id) waiting_task_count
             , a.wait_time_ms        - lag(a.wait_time_ms       ) over (partition by a.wait_type order by a.snap_id) wait_time_ms
             , datediff(second, lag(b.snap_time) over (partition by a.wait_type order by a.snap_id), b.snap_time) / 60.0 interval_minute
        from dbo.DBM_OS_WAITS  a
		     JOIN dbo.DBM_SNAP b on (b.Snap_id = a.snap_id) 
        where a.snap_id between $(vSnapIDStart) and $(vSnapIDEnd)
          and a.wait_type not in ('ABR','CLR_AUTO_EVENT','FT_IFTS_SCHEDULER_IDLE_WAIT')
        ) a
    where a.interval_minute is not null
;


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// dm_os_performance_counters
DBM_PERF_CNTR:
SQL select a.snap_id, a.object_name, a.counter_name, a.instance_name
       , a.cntr_value - lag(a.cntr_value) over (partition by a.object_name, a.counter_name, a.instance_name order by a.snap_id) cntr_value
	   , a.cntr_type
    from dbo.DBM_PERF_CNTR a
    where a.snap_id between $(vSnapIDStart) and $(vSnapIDEnd)
    ;
    
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// dm_exec_query_stats
DBM_SQLSTATS:
SQL select top 50000
           a.snap_id, a.sql_handle
         ---------------------------------------
         , a.execution_count_delta     
         , a.total_elapsed_time_delta  
         , a.total_worker_time_delta   
         , a.total_physical_reads_delta
         , a.total_logical_reads_delta 
         , a.total_logical_writes_delta
         ---------------------------------------
         , a.execution_count_delta       / b.interval_minutes  as execution_count_permin      
         , a.total_elapsed_time_delta    / b.interval_minutes  as total_elapsed_time_permin   
         , a.total_worker_time_delta     / b.interval_minutes  as total_worker_time_permin    
         , a.total_physical_reads_delta  / b.interval_minutes  as total_physical_reads_permin 
         , a.total_logical_reads_delta   / b.interval_minutes  as total_logical_reads_permin 
         , a.total_logical_writes_delta  / b.interval_minutes  as total_logical_writes_permin
         ---------------------------------------
         , sum(total_elapsed_time_delta) over (partition by a.sql_handle) total_elapsed_time_sum
         , c.text as sql_text
    from 
		(select snap_id, sql_handle
		     , (case when execution_count       >= execution_count_bf      then execution_count			- execution_count_bf      else  execution_count      end)				execution_count_delta                
		     , (case when total_elapsed_time    >= total_elapsed_time_bf   then total_elapsed_time  	- total_elapsed_time_bf   else 	total_elapsed_time   end) / 1000000.0	total_elapsed_time_delta  		
		     , (case when total_worker_time     >= total_worker_time_bf    then total_worker_time   	- total_worker_time_bf    else 	total_worker_time    end) / 1000000.0	total_worker_time_delta   		
		     , (case when total_physical_reads  >= total_physical_reads_bf then total_physical_reads	- total_physical_reads_bf else 	total_physical_reads end)				total_physical_reads_delta		
		     , (case when total_logical_reads   >= total_logical_reads_bf  then total_logical_reads 	- total_logical_reads_bf  else 	total_logical_reads  end)				total_logical_reads_delta 		
		     , (case when total_logical_writes  >= total_logical_writes_bf then total_logical_writes	- total_logical_writes_bf else 	total_logical_writes end)				total_logical_writes_delta		
			from (
		       select snap_id, sql_handle
		             , min(snap_id) over ()         min_snap_id
				     , sum(execution_count     )	execution_count 
					 , sum(total_elapsed_time  )    total_elapsed_time
					 , sum(total_worker_time   )	total_worker_time
					 , sum(total_physical_reads)    total_physical_reads
					 , sum(total_logical_reads )    total_logical_reads
					 , sum(total_logical_writes)    total_logical_writes
					 , lag(sum(execution_count		)) over (partition by sql_handle order by snap_id) execution_count_bf
					 , lag(sum(total_elapsed_time	)) over (partition by sql_handle order by snap_id) total_elapsed_time_bf
					 , lag(sum(total_worker_time	)) over (partition by sql_handle order by snap_id) total_worker_time_bf
					 , lag(sum(total_physical_reads	)) over (partition by sql_handle order by snap_id) total_physical_reads_bf
					 , lag(sum(total_logical_reads	)) over (partition by sql_handle order by snap_id) total_logical_reads_bf
					 , lag(sum(total_logical_writes	)) over (partition by sql_handle order by snap_id) total_logical_writes_bf
				from dbo.DBM_SQLSTATS a
				where a.snap_id between $(vSnapIDStart) -1 and $(vSnapIDEnd)
				  -- and sql_handle = 0x020000004D23C82FCBD9DFE3B7D06D0319388BAAC0CBDF7D0000000000000000000000000000000000000000
				group by snap_id, sql_handle
			   ) a
			where a.snap_id <> a.min_snap_id
		) a
        inner join (select snap_id
					     , datediff(second, lag(snap_time) over(order by snap_id), snap_time) / 60.0 as interval_minutes
					  from dbo.DBM_SNAP 
                   ) b  on (b.snap_id = a.snap_id)
	    left outer join dbo.DBM_SQLTEXT c on (c.sql_handle = a.sql_handle)
	where a.total_elapsed_time_delta > 0
    order by total_elapsed_time_sum desc
;

//MON_SQL_TEXT:
//SQL select sql_handle, text as sql_text from MON_SQL_TEXT where log_dt >= CONVERT(DATETIME,'$(vDateStart)', 120);