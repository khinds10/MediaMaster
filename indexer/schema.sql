CREATE TABLE IF NOT EXISTS `directories_list` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(255) DEFAULT NULL,
    `path` varchar(255) DEFAULT NULL,
    `parent_id` int(11) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `name` (`name`),
    KEY `path` (`path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
TRUNCATE TABLE directories_list;

CREATE TABLE IF NOT EXISTS `files_list` (
    `file_id` int(11) NOT NULL AUTO_INCREMENT,
    `full_path` varchar(255) DEFAULT NULL,
    `directory_name` varchar(255) DEFAULT NULL,
    `base_name` varchar(255) DEFAULT NULL,
    `ext` varchar(10) DEFAULT NULL,
    `file_name` varchar(255) DEFAULT NULL,
    `mime_type` varchar(255) DEFAULT NULL,
    `size` int(11) DEFAULT NULL,
    `date_accessed` date DEFAULT NULL,
    `date_modified` date DEFAULT NULL,
    `width` int(11) DEFAULT NULL,
    `height` int(11) DEFAULT NULL,
    `directory_id` int(11) DEFAULT NULL,
    `thumnail_exists` int(11) DEFAULT 0,
    PRIMARY KEY (`file_id`),
    KEY `file_name` (`file_name`),
    KEY `full_path` (`full_path`),
    KEY `directory_name` (`directory_name`),
    KEY `base_name` (`base_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
TRUNCATE TABLE files_list;

CREATE TABLE IF NOT EXISTS `text_list` (
    `text_id` int(11) NOT NULL AUTO_INCREMENT,
    `file_name` varchar(255) DEFAULT NULL,
    `contents` text DEFAULT NULL,
    `directory_id` int(11) DEFAULT NULL,
    `search_term` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`text_id`),
    KEY `file_name` (`file_name`),
    KEY `search_term` (`search_term`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
TRUNCATE TABLE text_list;
