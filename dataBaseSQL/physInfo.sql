-- ==========================================================
-- 使用者身體資訊明細檔資料表創建腳本
-- ==========================================================

-- 檢查主檔資料表是否存在，若不存在則發出警告
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'foodMaster')
BEGIN
    PRINT '警告：foodMaster 資料表不存在。請先執行 foodMaster.sql 創建主檔資料表。';
    RETURN;
END

-- 檢查身體資訊明細檔資料表是否存在，若不存在則建立
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'physInfo')
BEGIN
    CREATE TABLE physInfo (
        id INT IDENTITY(1,1) PRIMARY KEY, -- 明細檔的唯一ID
        master_id NVARCHAR(100) NOT NULL, -- 關聯到foodMaster的ID
        gender NVARCHAR(10), -- 性別
        age INT, -- 年齡
        height FLOAT, -- 身高(cm)
        weight FLOAT, -- 體重(kg)
        allergic_foods NVARCHAR(MAX), -- 過敏食物，以JSON格式儲存 ["蝦","花生","牛奶",...]
        createDate DATETIME DEFAULT GETDATE(), -- 資料建立日期時間
        updateDate DATETIME DEFAULT GETDATE(), -- 資料更新日期時間
        FOREIGN KEY (master_id) REFERENCES foodMaster(id) ON DELETE CASCADE
    );
    PRINT '已創建 physInfo 資料表';
END
ELSE
BEGIN
    PRINT 'physInfo 資料表已存在';
END

-- 檢查並建立索引
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_physInfo_master_id' AND object_id = OBJECT_ID(N'[dbo].[physInfo]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_physInfo_master_id] ON [dbo].[physInfo]
    (
        [master_id] ASC
    );
    PRINT '身體資訊明細檔主檔ID索引已建立';
END

-- 性能優化：複合索引 - 優化用戶更新查詢
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_physInfo_master_update' AND object_id = OBJECT_ID(N'[dbo].[physInfo]'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_physInfo_master_update] ON [dbo].[physInfo]
    (
        [master_id] ASC,
        [updateDate] DESC
    );
    PRINT '身體資訊主檔更新日期複合索引已建立';
END

-- 檢查並建立更新觸發器
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name='TR_physInfo_UpdateDate')
BEGIN
    EXEC('
    CREATE TRIGGER TR_physInfo_UpdateDate
    ON physInfo
    AFTER UPDATE
    AS
    BEGIN
        SET NOCOUNT ON;
        UPDATE physInfo
        SET updateDate = GETDATE()
        FROM physInfo p
        INNER JOIN inserted i ON p.id = i.id;
    END
    ');
    PRINT '身體資訊明細檔更新日期觸發器已建立';
END

PRINT '身體資訊明細檔資料表檢查和創建完成';
