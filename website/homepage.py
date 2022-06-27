import pathlib
import cv2
from shutil import copyfile
from datetime import date
from datetime import timedelta
import time
import os
import numpy as np
import math
import mysql.connector as mariadb
import sys
sys.path.insert(0, '/home/wesley/')
import server_info

# THIS SCRIPT IS AUTOMATED USING CRONJOB TO RUN EVERY DAY AT 12:00AM
def last24():
    today = date.today()
    non_string_yesterday = today - timedelta(days = 1)
    yesterday = str(non_string_yesterday)
    yesterday = yesterday.replace("/","-")
    print(yesterday)
    query = "SELECT PERMAID, XCOORD, YCOORD FROM Coordinate WHERE DATE LIKE '" + yesterday + "%';"
    print(query)

    #generic image for overlaying
    #eventually take in name of file
    im_path = pathlib.Path('./images/image2.jpg')
    image = cv2.imread(str(im_path))
    master_copy = image.copy()
    #draw lines using the database

    connection = server_info.connect_to_database()
    db_cursor = connection.cursor()
    db_cursor.execute(str(query))

    record = db_cursor.fetchall() # [0] = perma id, [1] = xcoord, [2] = ycoord
    #print(record)
    total_coords = []

    if len(record) < 1 or record is None:  #if record is empty
        print("No data available")
    else:
        perma_id = record[0][0]
        for row in record:
            if(row[0] != perma_id):
                perma_id = row[0]
                if(total_coords[0][1] > 1200):
                    master_color = (255,0,0)
                else:
                    master_color = (0,0,255)
                master_copy = cv2.polylines(master_copy, np.int32([total_coords]), False, master_color)
                total_coords.clear()
                coordinate = (row[1],row[2])
                total_coords.append(coordinate)
            else:
                coordinate = (row[1],row[2]) # tuple of the rows coordinates
                total_coords.append(coordinate) 

    db_cursor.close()

    if os.path.exists("./images/homepage.jpg"):
        os.remove("./images/homepage.jpg")

    cv2.imwrite('./images/homepage.jpg', master_copy)
    connection.close()

if __name__ == '__main__':
    last24()
