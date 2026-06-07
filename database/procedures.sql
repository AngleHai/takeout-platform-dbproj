USE `takeout`;

DROP PROCEDURE IF EXISTS `sp_AssignDelivery`;
DELIMITER ;;
CREATE PROCEDURE `sp_AssignDelivery`(
    IN  p_OrderID       CHAR(8),
    IN  p_DeliverymanID CHAR(8),
    IN  p_MerchantID    CHAR(8),
    OUT p_Result        VARCHAR(50)
)
BEGIN
    DECLARE v_Status        VARCHAR(20);
    DECLARE v_WorkStatus    CHAR(10);
    DECLARE v_CustomerPhone CHAR(13);

    SELECT `DeliveryStatus` INTO v_Status
    FROM `orders`
    WHERE `OrderID` = p_OrderID AND `MerchantID` = p_MerchantID;

    IF v_Status IS NULL THEN
        SET p_Result = '订单不存在或无权操作';
    ELSEIF v_Status != '已接单' THEN
        SET p_Result = '订单状态不可派单';
    ELSE
        SELECT `WorkStatus` INTO v_WorkStatus
        FROM `deliveryman` WHERE `UserID` = p_DeliverymanID;

        IF v_WorkStatus IS NULL THEN
            SET p_Result = '送餐员不存在';
        ELSEIF v_WorkStatus != '空闲' THEN
            SET p_Result = '送餐员当前不可用';
        ELSE
            SELECT u.`Phone` INTO v_CustomerPhone
            FROM `orders` o JOIN `user` u ON o.`CustomerID` = u.`UserID`
            WHERE o.`OrderID` = p_OrderID;

            DELETE FROM `logistics` WHERE `OrderID` = p_OrderID;
            INSERT INTO `logistics` (`OrderID`, `DeliverymanID`, `EstimatedTime`, `IsDelivered`, `CustomerPhone`)
            VALUES (p_OrderID, p_DeliverymanID, DATE_ADD(NOW(), INTERVAL 30 MINUTE), FALSE, v_CustomerPhone);

            SET p_Result = '派单成功';
        END IF;
    END IF;
END;;
DELIMITER ;
