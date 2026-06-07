-- ============================================================
-- 外卖平台管理系统 - 建表脚本
-- 数据库: takeout
-- ============================================================

CREATE DATABASE IF NOT EXISTS `takeout`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `takeout`;

-- ============================================================
-- 1. 用户表 User（ISA 父表）
-- ============================================================
DROP TABLE IF EXISTS `logistics`;
DROP TABLE IF EXISTS `order_dish`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `address`;
DROP TABLE IF EXISTS `dish`;
DROP TABLE IF EXISTS `deliveryman`;
DROP TABLE IF EXISTS `merchant`;
DROP TABLE IF EXISTS `customer`;
DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `UserID`   CHAR(8)      NOT NULL  COMMENT '用户ID',
  `UserName` CHAR(20)     NOT NULL  COMMENT '用户名',
  `Password` VARCHAR(20)  NOT NULL  COMMENT '密码，最少6位',
  `Phone`    CHAR(13)     DEFAULT NULL COMMENT '电话',
  `Role`     CHAR(10)     NOT NULL  COMMENT '角色：顾客/商家/送餐员',
  PRIMARY KEY (`UserID`),
  CONSTRAINT `chk_password_len` CHECK (CHAR_LENGTH(`Password`) >= 6),
  CONSTRAINT `chk_role` CHECK (`Role` IN ('顾客', '商家', '送餐员', '管理员'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 2. 顾客表 Customer（继承 User）
-- ============================================================
CREATE TABLE `customer` (
  `UserID`  CHAR(8)      NOT NULL  COMMENT '用户ID/主键/外键',
  `Name`    CHAR(20)     NOT NULL  COMMENT '姓名',
  `Gender`  CHAR(2)      DEFAULT NULL COMMENT '性别：男/女',
  `Age`     INT          DEFAULT NULL COMMENT '年龄',
  `Email`   VARCHAR(50)  DEFAULT NULL COMMENT '邮箱',
  PRIMARY KEY (`UserID`),
  CONSTRAINT `fk_customer_user` FOREIGN KEY (`UserID`) REFERENCES `user`(`UserID`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_gender` CHECK (`Gender` IN ('男', '女'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 3. 商家表 Merchant（继承 User）
-- ============================================================
CREATE TABLE `merchant` (
  `UserID`   CHAR(8)      NOT NULL  COMMENT '用户ID/主键/外键',
  `ShopName` VARCHAR(50)  DEFAULT NULL COMMENT '店铺名称',
  PRIMARY KEY (`UserID`),
  CONSTRAINT `fk_merchant_user` FOREIGN KEY (`UserID`) REFERENCES `user`(`UserID`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 4. 送餐员表 Deliveryman（继承 User）
-- ============================================================
CREATE TABLE `deliveryman` (
  `UserID`     CHAR(8)   NOT NULL  COMMENT '用户ID/主键/外键',
  `WorkStatus` CHAR(10)  NOT NULL  DEFAULT '空闲' COMMENT '工作状态',
  PRIMARY KEY (`UserID`),
  CONSTRAINT `fk_deliveryman_user` FOREIGN KEY (`UserID`) REFERENCES `user`(`UserID`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_work_status` CHECK (`WorkStatus` IN ('空闲', '配送中', '休息'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 5. 收货地址表 Address
-- ============================================================
CREATE TABLE `address` (
  `AddressID`     CHAR(8)      NOT NULL  COMMENT '地址ID',
  `CustomerID`    CHAR(8)      NOT NULL  COMMENT '所属顾客ID',
  `ReceiverName`  CHAR(20)     DEFAULT NULL COMMENT '收货人姓名',
  `ReceiverPhone` CHAR(13)     DEFAULT NULL COMMENT '收货人电话',
  `DetailAddress` VARCHAR(200) DEFAULT NULL COMMENT '详细地址',
  `IsDefault`     BOOLEAN      NOT NULL DEFAULT FALSE COMMENT '是否默认地址',
  PRIMARY KEY (`AddressID`, `CustomerID`),
  CONSTRAINT `fk_address_customer` FOREIGN KEY (`CustomerID`) REFERENCES `customer`(`UserID`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 6. 菜品表 Dish
-- ============================================================
CREATE TABLE `dish` (
  `DishID`     CHAR(8)       NOT NULL  COMMENT '菜品ID',
  `DishName`   VARCHAR(50)   NOT NULL  COMMENT '菜品名称',
  `Price`      DECIMAL(10,2) NOT NULL  COMMENT '菜品价格',
  `TotalSales` INT           NOT NULL  DEFAULT 0 COMMENT '总销量',
  `MerchantID` CHAR(8)       NOT NULL  COMMENT '所属商家ID',
  PRIMARY KEY (`DishID`),
  CONSTRAINT `fk_dish_merchant` FOREIGN KEY (`MerchantID`) REFERENCES `merchant`(`UserID`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_price` CHECK (`Price` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 7. 订单表 Orders
-- ============================================================
CREATE TABLE `orders` (
  `OrderID`        CHAR(8)       NOT NULL  COMMENT '订单ID',
  `CustomerID`     CHAR(8)       NOT NULL  COMMENT '顾客ID',
  `MerchantID`     CHAR(8)       NOT NULL  COMMENT '商家ID',
  `AddressID`      CHAR(8)       NOT NULL  COMMENT '收货地址ID',
  `OrderAmount`    DECIMAL(10,2) NOT NULL  DEFAULT 0 COMMENT '订单总金额',
  `PaymentMethod`  VARCHAR(20)   DEFAULT NULL COMMENT '支付方式',
  `OrderTime`      DATETIME      NOT NULL  COMMENT '下单时间',
  `DeliveryStatus` VARCHAR(20)   NOT NULL  DEFAULT '已接单' COMMENT '配送状态',
  PRIMARY KEY (`OrderID`),
  CONSTRAINT `fk_order_merchant` FOREIGN KEY (`MerchantID`) REFERENCES `merchant`(`UserID`),
  CONSTRAINT `chk_order_amount`  CHECK (`OrderAmount` >= 0),
  CONSTRAINT `chk_delivery_status` CHECK (`DeliveryStatus` IN ('已接单', '配送中', '已完成', '已取消'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 8. 订单-菜品关联表 OrderDish
-- ============================================================
CREATE TABLE `order_dish` (
  `OrderID`  CHAR(8) NOT NULL COMMENT '订单ID',
  `DishID`   CHAR(8) NOT NULL COMMENT '菜品ID',
  `Quantity` INT     NOT NULL COMMENT '购买数量',
  PRIMARY KEY (`OrderID`, `DishID`),
  CONSTRAINT `fk_od_order` FOREIGN KEY (`OrderID`) REFERENCES `orders`(`OrderID`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_od_dish`  FOREIGN KEY (`DishID`) REFERENCES `dish`(`DishID`),
  CONSTRAINT `chk_quantity` CHECK (`Quantity` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 9. 配送记录表 Logistics
-- ============================================================
CREATE TABLE `logistics` (
  `OrderID`        CHAR(8)  NOT NULL COMMENT '订单ID/主键/外键',
  `DeliverymanID`  CHAR(8)  NOT NULL COMMENT '送餐员ID',
  `EstimatedTime`  DATETIME DEFAULT NULL COMMENT '预计送达时间',
  `IsDelivered`    BOOLEAN  NOT NULL DEFAULT FALSE COMMENT '是否已送达',
  `CustomerPhone`  CHAR(13) DEFAULT NULL COMMENT '顾客电话',
  PRIMARY KEY (`OrderID`),
  CONSTRAINT `fk_logistics_order` FOREIGN KEY (`OrderID`) REFERENCES `orders`(`OrderID`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_logistics_deliveryman` FOREIGN KEY (`DeliverymanID`) REFERENCES `deliveryman`(`UserID`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
