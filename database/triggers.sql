-- ============================================================
-- 外卖平台管理系统 - 触发器 & 视图
-- ============================================================
USE `takeout`;

-- ============================================================
-- 触发器1: 插入订单菜品时自动更新 TotalSales
-- ============================================================
DROP TRIGGER IF EXISTS `trg_order_dish_after_insert`;
DELIMITER ;;
CREATE TRIGGER `trg_order_dish_after_insert`
AFTER INSERT ON `order_dish`
FOR EACH ROW
BEGIN
  UPDATE `dish`
  SET `TotalSales` = `TotalSales` + NEW.`Quantity`
  WHERE `DishID` = NEW.`DishID`;
END;;
DELIMITER ;

-- ============================================================
-- 触发器2: 删除订单菜品时回退 TotalSales
-- ============================================================
DROP TRIGGER IF EXISTS `trg_order_dish_after_delete`;
DELIMITER ;;
CREATE TRIGGER `trg_order_dish_after_delete`
AFTER DELETE ON `order_dish`
FOR EACH ROW
BEGIN
  UPDATE `dish`
  SET `TotalSales` = `TotalSales` - OLD.`Quantity`
  WHERE `DishID` = OLD.`DishID`;
END;;
DELIMITER ;

-- ============================================================
-- 触发器3: 配送员送达后自动更新订单状态为"已完成"
-- ============================================================
DROP TRIGGER IF EXISTS `trg_logistics_after_update`;
DELIMITER ;;
CREATE TRIGGER `trg_logistics_after_update`
AFTER UPDATE ON `logistics`
FOR EACH ROW
BEGIN
  IF NEW.`IsDelivered` = TRUE AND OLD.`IsDelivered` = FALSE THEN
    UPDATE `orders`
    SET `DeliveryStatus` = '已完成'
    WHERE `OrderID` = NEW.`OrderID`;

    -- 同时将配送员状态改为空闲
    UPDATE `deliveryman`
    SET `WorkStatus` = '空闲'
    WHERE `UserID` = NEW.`DeliverymanID`;
  END IF;
END;;
DELIMITER ;

-- ============================================================
-- 触发器4: 创建配送记录时将配送员状态改为"配送中"
-- ============================================================
DROP TRIGGER IF EXISTS `trg_logistics_after_insert`;
DELIMITER ;;
CREATE TRIGGER `trg_logistics_after_insert`
AFTER INSERT ON `logistics`
FOR EACH ROW
BEGIN
  UPDATE `deliveryman`
  SET `WorkStatus` = '配送中'
  WHERE `UserID` = NEW.`DeliverymanID`;

  -- 同时更新订单状态为"配送中"
  UPDATE `orders`
  SET `DeliveryStatus` = '配送中'
  WHERE `OrderID` = NEW.`OrderID`;
END;;
DELIMITER ;

-- ============================================================
-- 触发器5: 订单取消时，如果有配送记录，释放配送员
-- ============================================================
DROP TRIGGER IF EXISTS `trg_orders_after_update`;
DELIMITER ;;
CREATE TRIGGER `trg_orders_after_update`
AFTER UPDATE ON `orders`
FOR EACH ROW
BEGIN
  IF NEW.`DeliveryStatus` = '已取消' AND OLD.`DeliveryStatus` != '已取消' THEN
    UPDATE `deliveryman` d
    INNER JOIN `logistics` l ON l.`DeliverymanID` = d.`UserID`
    SET d.`WorkStatus` = '空闲'
    WHERE l.`OrderID` = NEW.`OrderID` AND l.`IsDelivered` = FALSE;
  END IF;
END;;
DELIMITER ;

-- ============================================================
-- 视图1: 订单详情视图（含顾客、商家、菜品信息）
-- ============================================================
DROP VIEW IF EXISTS `v_order_detail`;
CREATE VIEW `v_order_detail` AS
SELECT
  o.`OrderID`,
  o.`OrderTime`,
  o.`OrderAmount`,
  o.`PaymentMethod`,
  o.`DeliveryStatus`,
  c.`Name`       AS `CustomerName`,
  cu.`Phone`     AS `CustomerPhone`,
  m.`ShopName`   AS `MerchantName`,
  a.`DetailAddress`,
  a.`ReceiverName`,
  a.`ReceiverPhone`
FROM `orders` o
JOIN `customer` c  ON o.`CustomerID` = c.`UserID`
JOIN `user` cu     ON o.`CustomerID` = cu.`UserID`
JOIN `merchant` m  ON o.`MerchantID` = m.`UserID`
JOIN `address` a   ON o.`AddressID` = a.`AddressID` AND o.`CustomerID` = a.`CustomerID`;

-- ============================================================
-- 视图2: 商家销售统计视图
-- ============================================================
DROP VIEW IF EXISTS `v_merchant_stats`;
CREATE VIEW `v_merchant_stats` AS
SELECT
  m.`UserID`   AS `MerchantID`,
  m.`ShopName`,
  COUNT(DISTINCT o.`OrderID`) AS `TotalOrders`,
  IFNULL(SUM(o.`OrderAmount`), 0) AS `TotalRevenue`,
  COUNT(DISTINCT d.`DishID`) AS `DishCount`
FROM `merchant` m
LEFT JOIN `orders` o ON m.`UserID` = o.`MerchantID` AND o.`DeliveryStatus` != '已取消'
LEFT JOIN `dish` d   ON m.`UserID` = d.`MerchantID`
GROUP BY m.`UserID`, m.`ShopName`;

-- ============================================================
-- 视图3: 配送员工作统计视图
-- ============================================================
DROP VIEW IF EXISTS `v_deliveryman_stats`;
CREATE VIEW `v_deliveryman_stats` AS
SELECT
  dm.`UserID`     AS `DeliverymanID`,
  u.`UserName`    AS `DeliverymanName`,
  dm.`WorkStatus`,
  COUNT(CASE WHEN l.`IsDelivered` = TRUE THEN 1 END)  AS `CompletedDeliveries`,
  COUNT(CASE WHEN l.`IsDelivered` = FALSE THEN 1 END) AS `PendingDeliveries`
FROM `deliveryman` dm
JOIN `user` u      ON dm.`UserID` = u.`UserID`
LEFT JOIN `logistics` l ON dm.`UserID` = l.`DeliverymanID`
GROUP BY dm.`UserID`, u.`UserName`, dm.`WorkStatus`;
