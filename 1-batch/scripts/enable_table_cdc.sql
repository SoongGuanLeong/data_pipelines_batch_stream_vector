-- enable for all tables
USE AdventureWorks2022;
GO

DECLARE @sql NVARCHAR(MAX) = N'';

SELECT @sql += '
EXEC sys.sp_cdc_enable_table
  @source_schema = N''' + s.name + ''',
  @source_name   = N''' + t.name + ''',
  @role_name     = NULL;'
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE t.is_ms_shipped = 0 AND t.is_tracked_by_cdc = 0;

EXEC sp_executesql @sql;
GO
