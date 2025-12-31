-- ==========================================================
-- 食物明細檔資料表創建腳本
-- ==========================================================

-- 檢查主檔資料表是否存在，若不存在則發出警告
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'foodMaster')
BEGIN
    PRINT '警告：foodMaster 資料表不存在。請先執行 foodMaster.sql 創建主檔資料表。';
    RETURN;
END

-- 檢查明細檔資料表是否存在，若不存在則建立
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'foodDetails')
BEGIN
    CREATE TABLE foodDetails (
        id INT IDENTITY(1,1) PRIMARY KEY, -- 明細檔的唯一ID
        master_id NVARCHAR(100) NOT NULL, -- 關聯到foodMaster的ID
        intent NVARCHAR(50), -- 意圖（早餐、中餐、晚餐、點心）
        desc_text NVARCHAR(MAX), -- 食物描述
        calories INT, -- 卡路里
        total_calories INT, -- 今日共攝取卡路里
        createDate DATETIME DEFAULT GETDATE(), -- 資料建立日期時間
        FOREIGN KEY (master_id) REFERENCES foodMaster(id) ON DELETE CASCADE
    );
    PRINT '已創建 foodDetails 資料表';
END
ELSE
BEGIN
    PRINT 'foodDetails 資料表已存在';
END

-- 檢查並建立索引
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_foodDetails_master_id' AND object_id = OBJECT_ID(N'[dbo].[foodDetails]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_foodDetails_master_id] ON [dbo].[foodDetails]
    (
        [master_id] ASC
    );
    PRINT '食物明細主檔ID索引已建立';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_foodDetails_intent' AND object_id = OBJECT_ID(N'[dbo].[foodDetails]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_foodDetails_intent] ON [dbo].[foodDetails]
    (
        [intent] ASC
    );
    PRINT '食物明細意圖索引已建立';
END

-- 性能優化：複合索引 - 優化查詢性能，包含常用欄位
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_foodDetails_master_date' AND object_id = OBJECT_ID(N'[dbo].[foodDetails]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_foodDetails_master_date] ON [dbo].[foodDetails]
    (
        [master_id] ASC,
        [createDate] DESC
    ) INCLUDE ([intent], [desc_text], [calories], [total_calories]);
    PRINT '食物明細複合索引已建立';
END

-- 性能優化：建立日期索引
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_foodDetails_createDate' AND object_id = OBJECT_ID(N'[dbo].[foodDetails]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_foodDetails_createDate] ON [dbo].[foodDetails]
    (
        [createDate] DESC
    );
    PRINT '食物明細建立日期索引已建立';
END

PRINT '食物明細檔資料表檢查和創建完成';
