#/bin/bash
# version 0.01, 09-03-2018
# back up using rsync over ssh
# please make sure 
# 1) set up using ssh without typing the password or using a key.pem file
# 2) rsync is installed on both side and using the same protocol

echo 'start the bioku backup process ...'
#------------------------------------------- settings for this host on this side ----------------------------------------
echo 'auto create backup folders for the host on this side ...'
# target path
TGTPATH=$HOME
# bioku backup root folder name
BACKUPROOT="BIOKU_BACKUPS"
# backups in the sub folder
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
# complete path for backup
BACKUPFOLDER="$TGTPATH/$BACKUPROOT/$TIMESTAMP"
# sql file name
SQLFILENAME="bioku.sql"
# auto create if not found
if [ ! -d "$BACKUPFOLDER" ]; then
	mkdir -vp "$BACKUPFOLDER"
fi
#------------------------------------------- settings for the host running mysql server ----------------------------------------
REMOTESERVER="34.216.52.204"
echo "check the availability of the mysql server $REMOTESERVER ..."
# check the availability of the remote server
ping=$(ping -c 1 "$REMOTESERVER" 2>&1| grep "% packet" | cut -d" " -f 6 | tr -d "%")
if [ "$ping" = "" ]; then
	echo "Server $REMOTESERVER not reachable! The backup process has stopped!"
	exit
fi
echo "The remote mysql server $REMOTESERVER is reachable. Continue with the backup ..."
#------------------------------------------- settings for the backup ----------------------------------------
SSHPEM=true
SSHPEMPATH=$TGTPATH
SSHPEMNAME="buVM.pem"
SSHUSER="ubuntu"
MYSQLUSER="bioku"
MYSQLPSW="bioku"
MYSQLDATABASE="bioku"
MEDIAPATH="/usr/share/nginx/html/biodataware/media"
#------------------------------------------- backup mysql and media folder ----------------------------------------
if [ "$SSHPEM" = true ]; then
	# using the key pem file
	echo "ssh is configured to use a key file"
	echo "please make sure the key pem file can be found in $SSHPEMPATH/$SSHPEMNAME"
	# backup mysql database
	echo "start to backup the database ... "
	ssh -i "$SSHPEMPATH/$SSHPEMNAME" "$SSHUSER"@"$REMOTESERVER" "mysqldump -u $MYSQLUSER -p$MYSQLPSW $MYSQLDATABASE | gzip -3 -c" > "$BACKUPFOLDER/$SQLFILENAME"
	if [ $? -ne 0 ]; then 
		echo "the SQL database backup failed! The backup process has stopped! - $TIMESTAMP"
		exit
	fi
	# back media files
	echo "start to backup the media folder ... "
	rsync -aqz -e "ssh -i "$SSHPEMPATH/$SSHPEMNAME"" "$SSHUSER"@"$REMOTESERVER:$MEDIAPATH" "$BACKUPFOLDER"
	if [ $? -ne 0 ]; then 
		echo "the media folder backup failed! The backup process has stopped! - $TIMESTAMP"
		exit
	fi
else
	# not using the key pem file
	echo "ssh is not configured"
	echo "please make sure to set up using ssh without typing the password"
	# backup mysql database
	echo "start to backup the database ... "
	ssh "$SSHUSER"@"$REMOTESERVER" "mysqldump -u $MYSQLUSER -p$MYSQLPSW $MYSQLDATABASE | gzip -3 -c" > "$BACKUPFOLDER/$SQLFILENAME"
	if [ $? -ne 0 ]; then 
		echo "the SQL database backup failed! The backup process has stopped! - $TIMESTAMP"
		exit
	fi
	# back media files
	echo "start to backup the media folder ... "
	rsync -aqz -e ssh "$SSHUSER"@"$REMOTESERVER:$MEDIAPATH" "$BACKUPFOLDER"
	if [ $? -ne 0 ]; then 
		echo "the media folder backup failed! The backup process has stopped! - $TIMESTAMP"
		exit
	fi
fi
echo "the backup process finished with no error - $TIMESTAMP"
