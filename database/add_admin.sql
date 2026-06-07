-- ============================================================
-- 添加管理员角色
-- ============================================================
USE `takeout`;

-- 插入管理员账号（init.sql 中 CHECK 约束已包含 '管理员'）
-- 使用 IGNORE 避免重复执行报错
INSERT IGNORE INTO `user` (`UserID`, `UserName`, `Password`, `Phone`, `Role`)
VALUES ('U0000000', 'admin', '123456', NULL, '管理员');
