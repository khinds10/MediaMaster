#MediaMaster - Python Media File Indexed HTML5 WebApp

###UI Dependancies
	To install dependancies and build:

	Install "npm package manager" for the command line

	$ npm install
	$ grunt

###Python Dependancies

Required Packages:

	sudo apt-get install python-magic

	sudo apt-get install python-dev cython libavcodec-dev libavformat-dev libswscale-dev python-pip

	sudo pip install ffvideo

###Create MySQL Schema

Using a local instance of MySQL change the following lines to meet your local criteria for a database user that can create and access database tables.

Connect to your local MySQL instance and run the **indexer/schema.sql** against it, this should create your DB tables needed to index and query local media files on your system, indentified by the folder names above.

##Index your media files

in the file indexer/reindex.py update your settings to local values

	mediaFilesRoot = '/path/to/media/files'
	thumbnailSize = 256, 256
	thumbnailsRoot = '/path/to/media/files/thumbs'

Where **mediaFileRoot** is where you media files are located, **thumbnailsRoot** must be a local non-empty directory to place your thumbnails for each media file that is to be generated.

Also update the MySQL connection string to a local database connection with read/write permissions.

	db = MySQLdb.connect(host="localhost", user="user", passwd="password", db="media_master")

Now you can run your indexer to index media files.

	$ python ./indexer/reindex.py

*Note: If you would like to reindex at this time it's required you truncate the MySQL database tables first.*