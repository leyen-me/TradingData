-- 股票表
CREATE TABLE IF NOT EXISTS `t_stocks` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `stock_code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `stock_name` VARCHAR(50) NOT NULL COMMENT '股票名称',
    `market` VARCHAR(10) NOT NULL COMMENT '市场（SH/SZ/US）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_stock_code` (`stock_code`),
    KEY `idx_market` (`market`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基本信息表';

INSERT INTO `t_stocks` (`stock_code`, `stock_name`, `market`) VALUES
('TSLA.US', '特斯拉', 'US');
INSERT INTO `t_stocks` (`stock_code`, `stock_name`, `market`) VALUES
('TSLL.US', '特斯拉两倍做多', 'US');

-- 实时价格表
CREATE TABLE IF NOT EXISTS `t_quotes` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `stock_code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `last_done` DECIMAL(10, 3) NOT NULL COMMENT '最新价格',
    `open` DECIMAL(10, 3) NOT NULL COMMENT '开盘价',
    `high` DECIMAL(10, 3) NOT NULL COMMENT '最高价',
    `low` DECIMAL(10, 3) NOT NULL COMMENT '最低价',
    `volume` BIGINT NOT NULL COMMENT '成交量',
    `turnover` DECIMAL(20, 3) NOT NULL COMMENT '成交额',
    `trade_status` VARCHAR(20) NOT NULL COMMENT '交易状态',
    `current_volume` BIGINT NOT NULL COMMENT '当前成交量',
    `current_turnover` DECIMAL(20, 3) NOT NULL COMMENT '当前成交额',
    `timestamp` DATETIME NOT NULL COMMENT '最新价格时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_stock_code` (`stock_code`),
    KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实时行情表';

-- 实时成交表
CREATE TABLE IF NOT EXISTS `t_trades` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `stock_code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `price` DECIMAL(10, 3) NOT NULL COMMENT '成交价',
    `volume` BIGINT NOT NULL COMMENT '成交量',
    `trade_type` VARCHAR(10) NOT NULL COMMENT '成交类型',
    `direction` VARCHAR(500) NOT NULL COMMENT '成交方向',
    `timestamp` DATETIME NOT NULL COMMENT '成交时间',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_stock_code` (`stock_code`),
    KEY `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实时成交表';

-- 实时盘口表
CREATE TABLE IF NOT EXISTS `t_depths` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `stock_code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `position` INT NOT NULL COMMENT '档位',
    `price` DECIMAL(10, 3) NOT NULL COMMENT '价格',
    `volume` BIGINT NOT NULL COMMENT '数量',
    `order_num` INT NOT NULL COMMENT '订单数量',
    `type` VARCHAR(10) NOT NULL COMMENT '类型(ask/bid)',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_stock_code` (`stock_code`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实时盘口表';

