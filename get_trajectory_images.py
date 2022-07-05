import paramiko
import mysql.connector as mariadb
import os, glob, os.path

import sys
sys.path.insert(0, '/home/wesley/')
import server_info

def download_files(person_id):
    
    #connect to mariadb
    connection = server_info.connect_to_database()
    db_cursor = connection.cursor()
    db_cursor.execute("select PATH from Frame where DATE in (select DATE from Contains where PERMAID=%s);", [person_id])
    record = db_cursor.fetchall()

    #connect to hartley w/ paramiko
    hartley = server_info.connect_to_hartley()
    ftp_client = hartley.open_sftp()

    if len(record) < 1:
        print("None")
        return
    else:
        #remove every file in the debug directory
        files = glob.glob(os.path.join("/var/www/html/images/debug_images", "*.jpg"))
        for file in files:
            os.remove(file)

        #populate the directory with new files from hartley
        for row in record:
            basename = os.path.basename(row[0])
            filepath = "/var/www/html/images/debug_images/" + basename
            ftp_client.get(row[0], filepath)

    return

if __name__ == "__main__":
    download_files(sys.argv[1])
