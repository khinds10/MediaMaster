# MediaMaster - Python Media File Indexed HTML5 WebApp

### UI Dependancies
	To install dependancies and build:

	Install "npm package manager" for the command line

	$ npm install
	$ grunt

### Python Dependancies

Required Packages:

	sudo apt-get install python-magic

	sudo apt-get install python-dev cython libavcodec-dev libavformat-dev libswscale-dev python-pip

	sudo -H pip install ffvideo
	
	sudo pip install opencv-python

### Create MySQL Schema

```
CREATE DATABASE media_master;
USE media_master;

CREATE TABLE `directories_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`),
  KEY `path` (`path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `files_list` (
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
  PRIMARY KEY (`file_id`),
  KEY `file_name` (`file_name`),
  KEY `full_path` (`full_path`),
  KEY `directory_name` (`directory_name`),
  KEY `base_name` (`base_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `text_list` (
  `text_id` int(11) NOT NULL AUTO_INCREMENT,
  `file_name` varchar(255) DEFAULT NULL,
  `contents` text,
  `directory_id` int(11) DEFAULT NULL,
  `search_term` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`text_id`),
  KEY `file_name` (`file_name`),
  KEY `search_term` (`search_term`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

Using a local instance of MySQL change the following lines to meet your local criteria for a database user that can create and access database tables.

Connect to your local MySQL instance and run the **indexer/schema.sql** against it, this should create your DB tables needed to index and query local media files on your system, indentified by the folder names above.

## Index your media files

in the file indexer/reindex.py update your settings to local values

	mediaFilesRoot = '/path/to/media/files'
	thumbnailSize = 256, 256
	thumbnailsRoot = '/path/to/media/files/thumbs'

Where **mediaFileRoot** is where you media files are located, **thumbnailsRoot** must be a local empty folder to place your thumbnails for each media file that is to be generated.  This folder path must be inside of this web application.

Also update the MySQL connection string to a local database connection with read/write permissions.

	db = MySQLdb.connect(host="localhost", user="user", passwd="password", db="media_master")

Now you can run your indexer to index media files.

	$ python ./indexer/reindex.py

*Note: If you would like to reindex at this time it's required you truncate the MySQL database tables first.*

### Apache2 Config for Python CGI

	<VirtualHost *:80>
		ServerName mediamaster
		ServerAlias mediamaster
		ServerAdmin admin@mediamaster
		DocumentRoot /var/www/MediaMaster
		<Directory /var/www/MediaMaster>
			Options FollowSymLinks
			AllowOverride All
			Require all granted
		</Directory>
		<Directory /var/www/MediaMaster/indexer>
			Options FollowSymLinks
			AllowOverride All
			Require all granted
	    	Options Indexes FollowSymLinks MultiViews ExecCGI
	    	SetHandler cgi-script
		</Directory>
	</VirtualHost>
