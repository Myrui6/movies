CREATE TABLE `administrator` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  INDEX `idx_admin_name` (`name`)
);


CREATE TABLE `user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL,
  `password` VARCHAR(100) NOT NULL,
  INDEX `idx_user_name` (`name`)
);


CREATE TABLE `movie` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(45) NOT NULL,
  `picture` LONGBLOB,
  `type` VARCHAR(45) NOT NULL,
  `region` VARCHAR(45) NOT NULL,
  `time` INT NOT NULL,
  `brief` TEXT,
  INDEX `idx_movie_name` (`name`)
);


CREATE TABLE `hall` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL UNIQUE,
  `total_rows` INT NOT NULL,
  `total_columns` INT NOT NULL,
  INDEX `idx_hall_name` (`name`)
);


CREATE TABLE `schedule` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `movie_id` INT NOT NULL,
  `hall_id` INT NOT NULL,
  `start_time` DATETIME NOT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (`movie_id`) REFERENCES `movie`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`hall_id`) REFERENCES `hall`(`id`),
  INDEX `idx_schedule_time` (`start_time`),
  INDEX `idx_schedule_movie` (`movie_id`),
  INDEX `idx_schedule_hall` (`hall_id`),
  INDEX `idx_schedule_movie_time` (`movie_id`, `start_time`)
);


CREATE TABLE `seat` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `schedule_id` INT NOT NULL,
  `row_num` INT NOT NULL,
  `col_num` INT NOT NULL,
  `state` TINYINT NOT NULL DEFAULT 0 COMMENT '0:可选, 1:已售, 2:锁定',
  FOREIGN KEY (`schedule_id`) REFERENCES `schedule`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `unique_seat_per_schedule` (`schedule_id`, `row_num`, `col_num`),
  INDEX `idx_seat_schedule` (`schedule_id`),
  INDEX `idx_seat_state` (`state`)
);


CREATE TABLE `order` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `schedule_id` INT NOT NULL,
  `seat_details` TEXT NOT NULL,
  `total_price` DECIMAL(10,2) NOT NULL,
  `state` INT NOT NULL DEFAULT 0,
  `reason` VARCHAR(255),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`),
  FOREIGN KEY (`schedule_id`) REFERENCES `schedule`(`id`),
  INDEX `idx_order_user` (`user_id`),
  INDEX `idx_order_schedule` (`schedule_id`),
  INDEX `idx_order_state` (`state`)
);