-- ==========================================================
-- 食物主檔資料表創建腳本
-- ==========================================================

-- 檢查主檔資料表是否存在，若不存在則建立
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'foodMaster')
BEGIN
    CREATE TABLE foodMaster (
        id NVARCHAR(100) PRIMARY KEY, -- 使用LineWebHookRESTController中image存檔的名稱(不含附檔名)
        createDate DATETIME DEFAULT GETDATE(), -- 資料建立日期時間
        user_id NVARCHAR(100) -- 與user關聯的ID
    );
    PRINT '已創建 foodMaster 資料表';
END
ELSE
BEGIN
    PRINT 'foodMaster 資料表已存在';
END

-- 檢查並建立索引
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_foodMaster_user_id' AND object_id = OBJECT_ID(N'[dbo].[foodMaster]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_foodMaster_user_id] ON [dbo].[foodMaster]
    (
        [user_id] ASC
    );
    PRINT '食物主檔用戶ID索引已建立';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_foodMaster_createDate' AND object_id = OBJECT_ID(N'[dbo].[foodMaster]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_foodMaster_createDate] ON [dbo].[foodMaster]
    (
        [createDate] DESC
    );
    PRINT '食物主檔建立日期索引已建立';
END

-- 性能優化：複合索引 - 優化用戶查詢性能
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_foodMaster_user_date' AND object_id = OBJECT_ID(N'[dbo].[foodMaster]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_foodMaster_user_date] ON [dbo].[foodMaster]
    (
        [user_id] ASC,
        [createDate] DESC
    );
    PRINT '食物主檔用戶日期複合索引已建立';
END

PRINT '食物主檔資料表檢查和創建完成';
