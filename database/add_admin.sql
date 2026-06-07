-- ============================================================
-- 添加管理员角色
-- ============================================================
USE `takeout`;

-- 1. 删除原有 Role 约束，添加新的（包含管理员）
ALTER TABLE `user` DROP CONSTRAINT `chk_role`;
ALTER TABLE `user` ADD CONSTRAINT `chk_role` CHECK (`Role` IN ('顾客', '商家', '配送员', '管理员'));

-- 2. 插入管理员账号
INSERT INTO `user` (`UserID`, `UserName`, `Password`, `Phone`, `Role`)
VALUES ('U0000000', 'admin', '123456', NULL, '管理员');
