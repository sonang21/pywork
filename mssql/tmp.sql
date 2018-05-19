


[oracle:/etc]% df -m
Filesystem           1M-blocks   Used Available Use% Mounted on
/dev/sda3               273191  64729    194579  25% /
tmpfs                    80632     25     80607   1% /dev/shm
/dev/sda1                  190     65       116  36% /boot
/dev/sdb1               563034     71    534357   1% /orabackup
/dev/mapper/VG10-engn01
                         50265  31690     16015  67% /engn001
/dev/mapper/VG11-data001
                        503835 376644    101592  79% /data01
/dev/mapper/VG12-data002
                        503835 345227    133008  73% /data02
/dev/mapper/VG13-data003
                        503835 353227    125008  74% /data03
/dev/mapper/VG14-data004
                        503835 368170    110065  77% /data04
/dev/mapper/VG15-data005
                        503835 346170    132065  73% /data05
/dev/mapper/VG16-data006
                        503835 346070    132165  73% /data06
/dev/mapper/VG17-data007
                        503835 381070     97165  80% /data07
/dev/mapper/VG18-arch001
                        503835 287287    190949  61% /oraarch
[oracle:/engn001/oracle/product/11.2.0/dbs]% cat initORCL.ora
*.audit_file_dest='/engn001/oracle/admin/ORCL/adump'
*.audit_trail='db'
*.compatible='11.2.0.0.0'
*.control_files='/data01/ORCL/system/control01.ctl','/data02/ORCL/system/control02.ctl','/data03/ORCL/system/control03.ctl'
*.db_block_size=8192
*.db_domain=''
*.db_name='ORCL'
*.db_writer_processes=10
*.db_recovery_file_dest='/data01/ORCL'
*.db_recovery_file_dest_size=5218762752
*.diagnostic_dest='/engn001/oracle'
*.dispatchers='(PROTOCOL=TCP) (SERVICE=ORCLXDB)'
*.log_buffer=20971520
#*.memory_target=67637346304
#*.memory_target=110G
*.open_cursors=10000
*.pga_aggregate_target=35000m
*.processes=3200
*.remote_login_passwordfile='EXCLUSIVE'
*.session_cached_cursors=1000
*.sessions=4000
*.sga_target=72G
*.undo_tablespace='UNDOTBS1'
*.log_archive_dest_1="location=/oraarch"
*.log_archive_format=arch_%t_%s_%r.arc
*.use_large_pages=only

#20170408 undo parameter add
*.undo_retention=18000
*._undo_autotune=false

#20171020 parameter add
*.filesystemio_options=ASYNCH
*._add_col_optim_enabled=FALSE
*._PX_use_large_pool=TRUE
*._in_memory_undo=FALSE
*._row_cache_cursors=1000
*._partition_large_extents=FALSE
*._index_partition_large_extents=FALSE

[oracle:/engn001/oracle/product/11.2.0/dbs]%
