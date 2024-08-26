CREATE TABLE IF NOT EXISTS `file_path_info`  (
  `id` INT AUTO_INCREMENT PRIMARY KEY UNIQUE COMMENT '主键id',
  `user` VARCHAR(20) NOT NULL  COMMENT '用户',
  `path` VARCHAR(255) NOT NULL COMMENT '本次操作文件路径',
  `former_path` VARCHAR(255) DEFAULT NULL COMMENT '旧文件路径',
  `type` VARCHAR(10) NOT NULL COMMENT '类型',
  `status` VARCHAR(10) NOT NULL COMMENT '状态',
  `ip` VARCHAR(15) NOT NULL COMMENT 'IP地址',
  `info` VARCHAR(20) NULL DEFAULT '无' COMMENT '操作信息',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='文件路径信息操作详情表';

CREATE TABLE `file_path`  (
  `path` varchar(255) NOT NULL UNIQUE PRIMARY KEY COMMENT '文件路径',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='文件路径信息表';

CREATE TABLE `username`  (
  `user` varchar(20) NOT NULL PRIMARY KEY UNIQUE COMMENT '用户' ,
  `password` varchar(64) NOT NULL COMMENT '密码',
  `is_start` TINYINT(1) NOT NULL  DEFAULT 0 COMMENT '是否启用账号，0:代表启用 1:代表不启用',
  `username` varchar(20) NULL COMMENT '用户名称',
  `power` varchar(10) NULL COMMENT '用户权限（保留扩展使用）',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='用户表';

CREATE TABLE `check_file_type`  (
  `id` INT AUTO_INCREMENT PRIMARY KEY UNIQUE COMMENT '主键id',
  `is_start` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否启用 0代表允许 1 代表不允',
  `file_type` varchar(15) NOT NULL UNIQUE COMMENT '文件类型',
  `file_type_descr` varchar(50) NULL COMMENT '文件类型备注',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='允许的文件后缀';

CREATE TABLE `login_attempts` (
  `user` varchar(20) NOT NULL PRIMARY KEY UNIQUE COMMENT '用户',
  `attempts` TINYINT(3) NOT NULL DEFAULT 0  COMMENT '尝试次数',
  `last_attempt_time` DATETIME DEFAULT NULL  COMMENT '最后一次尝试时间',
  `permit_max` TINYINT(3) NOT NULL DEFAULT 5 COMMENT '允许最大尝试次数',
  `is_locked` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否锁定 0代表锁定 1 代表不锁定',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='登录次数限制表' ;


CREATE TABLE `ip_whitelist` (
  `ip_address` VARCHAR(15) NOT NULL PRIMARY KEY COMMENT 'IP地址',
  `is_ip` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否启用 0代表白名单 1 代表黑名单',
  `update` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='IP黑白名单表';


INSERT INTO `username` (`user`, `password`, `username`, `power`)
VALUES ('admin', 'password', '管理员', 'admin');