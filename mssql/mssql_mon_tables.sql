IF OBJECT_ID('dbo.DBM_SNAP', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_SNAP;
    
CREATE TABLE dbo.DBM_SNAP (
      Snap_id               bigint      NOT NULL 
    , Snap_time             datetime    NOT NULL
    , Local_time            datetime
    , CONSTRAINT PK_DBM_SNAP PRIMARY KEY CLUSTERED (Snap_id) ON [PRIMARY]
) ON [PRIMARY]
;
GO


IF OBJECT_ID('dbo.DBM_STATS', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_STATS;

CREATE TABLE dbo.DBM_STATS(
      Snap_Id               bigint      NOT NULL
    ------------------------------
    , CPU_Busy              bigint
    , CPU_Total             bigint
    , Locks_ms              bigint
    , Reads_ms              bigint
    , Writes_ms             bigint
    , Networks_ms           bigint
    , Backups_ms            bigint
    , Cursors_ms            bigint
    , DISK_IO_ms            bigint
    , LockInfo_ms           bigint
    , Memory_ms             bigint
    , Latch_Page_ms         bigint
    , Latch_PageIo_ms       bigint
    , Latch_PageAll_ms      bigint
    , Latch_Others_ms       bigint
    , Latch_Tran_ms         bigint 
    , Others_ms             bigint 
    , SqlCompile_ms         bigint
    , Tran_Log_ms           bigint
    , PhysicalReads_cnt     bigint
    , PhysicalWrites_cnt    bigint
    ------------------------------
    , LogicalReads_cnt      bigint
    , BatchRequest_cnt      bigint
    , SqlCompile_cnt        bigint
    , SqlRecompile_cnt      bigint
    , Transaction_cnt       bigint
    ------------------------------
    , CPU                   bigint
    ---------------------------------------------------------------------
    , CONSTRAINT PK_DBM_STATS PRIMARY KEY CLUSTERED (Snap_Id) ON [PRIMARY]
) ON [PRIMARY]
;
GO

--------------------------------------------------------------------------------

IF OBJECT_ID('dbo.DBM_PERF_CNTR', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_PERF_CNTR;

CREATE TABLE dbo.DBM_PERF_CNTR(
      Snap_Id               bigint      NOT NULL
    ------------------------------
    , object_name           nvarchar(256)
    , counter_name          nvarchar(256)
    , instance_name         nvarchar(256)
    , cntr_value            bigint
    , cntr_type             int
    ---------------------------------------------------------------------
    , CONSTRAINT PK_DBM_PERF_CNTR PRIMARY KEY CLUSTERED (Snap_Id, object_name, counter_name, instance_name) ON [PRIMARY]
) ON [PRIMARY]
;
GO


--------------------------------------------------------------------------------

IF OBJECT_ID('dbo.DBM_SESSIONS', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_SESSIONS;

CREATE TABLE dbo.DBM_SESSIONS(
      Snap_Id                       bigint      NOT NULL
    , session_id                    smallint
    , login_time                    datetime
    , last_request_start_time       datetime
    , last_request_end_time         datetime
    ------------------------------
    , host_name                     nvarchar(256)
    , login_name                    nvarchar(256)
    , program_name                  nvarchar(256)
    , client_interface_name         nvarchar(64)
    , status                        nvarchar(60)
    ------------------------------
    , total_elapsed_time            bigint
    , reads                         bigint
    , writes                        bigint
    , logical_reads                 bigint
    , row_count                     bigint
    ------------------------------
    , open_transaction_count        int
      ---------------------------------------------------------------------
    , CONSTRAINT PK_DBM_SESSIONS PRIMARY KEY CLUSTERED (snap_id, session_id) ON [PRIMARY]
) ON [PRIMARY]
;
GO

--------------------------------------------------------------------------------
IF OBJECT_ID('dbo.DBM_REQUESTS', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_REQUESTS;

CREATE TABLE dbo.DBM_REQUESTS (
      Snap_Id                       bigint      NOT NULL
    , session_id                    smallint
    , request_id                    int
    , start_time                    datetime
    , total_elapsed_time            int
    ------------------------------
    , status                        nvarchar(60)
    , command                       nvarchar(64)
    , sql_handle                    varbinary(64)
    , statement_start_offset        int
    , statement_end_offset          int
    ------------------------------
    , statement_sql_handle          varbinary(64)
    , blocking_session_id           smallint
    , wait_type                     nvarchar(120)
    , wait_time                     int
    , last_wait_type                nvarchar(120)
    ------------------------------
    , wait_resource                 nvarchar(512)
    , percent_complete              real
    , estimated_completion_time     bigint
    , cpu_time                      int
    , logical_reads                 bigint
    ------------------------------
    ---------------------------------------------------------------------
    , CONSTRAINT PK_DBM_REQUESTS PRIMARY KEY CLUSTERED (snap_id, session_id, request_id) ON [PRIMARY]
) ON [PRIMARY]
;
GO


--------------------------------------------------------------------------------
IF OBJECT_ID('dbo.DBM_SQLSTATS', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_SQLSTATS;

CREATE TABLE dbo.DBM_SQLSTATS (    
      Snap_Id                       bigint      NOT NULL
    , sql_handle                    varbinary(64)
    , statement_start_offset        int
    , statement_end_offset          int
    , plan_generation_num           bigint
    ------------------------------
    , plan_handle                   varbinary(64)
    , creation_time                 datetime
    , last_execution_time           datetime
    , execution_count               bigint
    , total_worker_time             bigint
    ------------------------------
    , max_worker_time               bigint
    , total_physical_reads          bigint
    , max_physical_reads            bigint
    , total_logical_writes          bigint
    , max_logical_writes            bigint
    ------------------------------
    , total_logical_reads           bigint
    , max_logical_reads             bigint
    , total_clr_time                bigint
    , max_clr_time                  bigint
    , total_elapsed_time            bigint
    ------------------------------
    , max_elapsed_time              bigint
    , total_rows                    bigint
    , max_rows                      bigint
    ---------------------------------------------------------------------
    , CONSTRAINT PK_DBM_SQLSTATS PRIMARY KEY CLUSTERED (snap_id, sql_handle, statement_start_offset, plan_handle) ON [PRIMARY]
) ON [PRIMARY]
;
GO

--------------------------------------------------------------------------------
IF OBJECT_ID('dbo.DBM_SQLTEXT', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_SQLTEXT;

CREATE TABLE dbo.DBM_SQLTEXT (    
      sql_handle                    varbinary(64)
    , dbname                        nvarchar(256)
    , objectname                    nvarchar(256)
    , text                          nvarchar(max)
    , log_dt                        datetime
    ---------------------------------------------------------------------
    , CONSTRAINT PK_DBM_SQLTEXT PRIMARY KEY CLUSTERED (sql_handle) ON [PRIMARY]
) ON [PRIMARY]
;
GO


--##############################################################################
--
IF OBJECT_ID('dbo.DBM_TABSIZE', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_TABSIZE;

CREATE TABLE dbo.DBM_TABSIZE (    
      Snap_Id                       bigint      NOT NULL
    , dbname                        nvarchar(256)
    , schema_name                   nvarchar(256)
    , table_name                    nvarchar(256)
    , log_dt                        datetime
    , num_rows                      bigint
    , data_mb                       numeric(26,6)
    , index_mb                      numeric(26,6)
    , used_mb                       numeric(26,6)
    , unused_mb                     numeric(26,6)
    , reserved_mb                   numeric(26,6)
    ---------------------------------------------------------------------
    , CONSTRAINT PK_DBM_TABSIZE PRIMARY KEY CLUSTERED (Snap_id, dbname, schema_name, table_name) ON [PRIMARY]
) ON [PRIMARY]
;
GO


--##############################################################################
--
IF OBJECT_ID('dbo.DBM_ACTIONS', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_ACTIONS;

CREATE TABLE dbo.DBM_ACTIONS (    
      Snap_Id                       bigint      NOT NULL
    , session_id                    smallint
    , block_spid                    smallint
    , query_text                    nvarchar(max)
    , program_name                  nvarchar(256)
    , host_name                     nvarchar(256)
    , client_net_address            varchar(48)
    , elapsed_time_hms              varchar(14)
    , total_elapsed_time            int
    , cpu_time                      int
    , logical_reads                 bigint
    , reads                         bigint
    , writes                        bigint
    , text                          nvarchar(max)
    , status                        nvarchar(60)
    , wait_type                     nvarchar(120)
    , start_time                    datetime 
    , plan_handle                   varbinary(64)
    , log_dt                        datetime
    ---------------------------------------------------------------------
    , CONSTRAINT PK_DBM_ACTIONS PRIMARY KEY CLUSTERED (snap_id, session_id) ON [PRIMARY]
) ON [PRIMARY]
;
GO

--##############################################################################
--
IF OBJECT_ID('dbo.DBM_OS_WAITS', 'U') IS NOT NULL 
    DROP TABLE dbo.DBM_OS_WAITS;

CREATE TABLE dbo.DBM_OS_WAITS (    
      Snap_Id                       bigint      NOT NULL
    , wait_type                     nvarchar(120)
    , waiting_tasks_count           bigint
    , wait_time_ms                  bigint
    , max_wait_time_ms              bigint
    , signal_wait_time_ms           bigint
    ---------------------------------------------------------------------
    , CONSTRAINT PK_DBM_OS_WAITS PRIMARY KEY CLUSTERED (snap_id, wait_type) ON [PRIMARY]
) ON [PRIMARY]
;
GO



