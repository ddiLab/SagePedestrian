import pathlib
import cv2
from shutil import copyfile
from datetime import datetime
import time
import sqlite3
import os
import sys
import numpy as np
from matplotlib import pyplot as pt

def main(query):
    #generic image for overlaying
    #eventually take in name of file
    im_path = pathlib.Path('/var/www/html/images/image2.jpg')
    image = cv2.imread(str(im_path))
    master_copy = image.copy()
    #print(query)
    #print(str(im_path)) # MUST PRINT HERE OR ELSE WE DO NOT GET THE OUTPUT OF IMAGE PATH BACK INTO THE PHP FILE
    #draw lines using the database

    db_path = "/home/justind/Website/pedestrian_detections.db"
    db_connection = sqlite3.connect(db_path)
    db_cursor = db_connection.cursor()
    db_cursor.execute(str(query))
    record = db_cursor.fetchall() # [0] = perma id, [1] = xcoord, [2] = ycoord

    total_coords = []
    #perma_id = record[0][0] # get first perma id for the day

    #print("something")

    #print(str(len(record)))

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
    total_coords.clear()
#    cv2.putText(master_copy, "East", (500,120), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,0,255),6)
#    cv2.putText(master_copy, "West", (500,260), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,0,0),6)

    if os.path.exists("/var/www/html/images/user_img.jpg"):
        os.remove("/var/www/html/images/user_img.jpg")

    cv2.imwrite('/var/www/html/images/user_img.jpg', master_copy)
    db_connection.close()

if __name__ == '__main__':
    main(sys.argv[1])
