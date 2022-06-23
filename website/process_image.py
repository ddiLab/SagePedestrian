from audioop import cross
import pathlib
import cv2
from shutil import copyfile
from datetime import datetime
import time
import sqlite3
import os
import sys
import numpy as np

def pi_chart_per_hour(db_cursor, date):
    from matplotlib import pyplot as pie
    #crosswalk uses per hour for sepcific 'date'
    query2 = "select count(distinct PERMAID) from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK==1 intersect select distinct PERMAID from Contains where DATE like \'" + date + "%\') group by strftime(\'%H\', DATE);"
    #total number of crosswalk uses for 1 day
    db_cursor.execute(query2)
    hours = [13-5, 14-5, 15-5, 16-5, 17-5, 18-5, 19-5, 20-5, 21-5, 22-5]
    results = db_cursor.fetchall()
    pie_labels = ["8am", "9am", "10am", "11am", "12pm", "1pm" , "2pm", "3pm", "4pm", "5pm"]
    #format results
    hourly_xwalk_data = []
    for row in results:
        hourly_xwalk_data.append(row[0])
    print(hourly_xwalk_data)
    pie.title('Crosswalk usages per hour for ' + str(date))
    pie.pie(hourly_xwalk_data, labels = pie_labels)
    pie.savefig('/var/www/html/images/xwalk_pie_per_hr.png')
    pie.clf()

    return

def uses_per_hour(db_cursor, date):
    from matplotlib import pyplot as plt
    query2 = "select count(distinct PERMAID) from Contains where PERMAID in (select PERMAID from Person where USEROAD==1 intersect select distinct PERMAID from Contains where DATE like \'" + date + "%\') group by strftime(\'%H\', DATE);"
    db_cursor.execute(query2)
    road_results = db_cursor.fetchall()
    query3 = "select count(distinct PERMAID) from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK==1 intersect select distinct PERMAID from Contains where DATE like \'" + date + "%\') group by strftime(\'%H\', DATE);"
    db_cursor.execute(query3)
    cwalk_results = db_cursor.fetchall()
    #format results
    hours = [13-5, 14-5, 15-5, 16-5, 17-5, 18-5, 19-5, 20-5, 21-5, 22-5]
    hourly_cwalk_data = []
    hourly_road_data = []

    for res in cwalk_results:
        hourly_cwalk_data.append(res[0])
    print(hourly_cwalk_data)
    for res in road_results:
        hourly_road_data.append(res[0])
    print(hourly_road_data)

    x = np.arange(len(hours)) # label locations
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar( x- width/2, hourly_cwalk_data, width, label="Crosswalk")
    rects2 = ax.bar(x + width/2, hourly_road_data, width, label="Road")
    ax.set_ylabel('Uses')
    ax.set_xlabel('Hours')
    ax.set_title('Number of Crosswalk and Road Uses Per Hour ' + str(date))
    ax.set_xticks(x, hours)
    ax.legend()
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    fig.tight_layout()
    plt.savefig('/var/www/html/images/uses_per_hour.png')

    return

def heatmap_per_hour(db_cursor, date):
    from matplotlib import pyplot as plt
    query2 = "select count(distinct PERMAID), strftime('%Y-%m-%d', DATE) as day, strftime('%H', DATE) as hour from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK==1 intersect select distinct PERMAID from Contains) group by hour,day order by day;"
    db_cursor.execute(query2)
    heatmap_raw = db_cursor.fetchall()
    #format results
    counts = []
    hours = []
    days = []

    print("QUery successful")

    for result in heatmap_raw:
        days.append(result[1])

    for i in range(13, 23, 1):
        hours.append(i)

    for i in range(len(days)):
        x = []
        counts.append(x)
    
    row_count = 0
    while row_count < len(days):
        for result in heatmap_raw:
            counts[row_count].append(result[0])
        row_count += 1

    print(days)
    print(hours)
    print(counts)

    return

    fig, ax = plt.subplots()
    ax.set_xticks(np.arrange(len(days)), days)
    ax.set_yticks(np.arrange(len(hours)), hours)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    ax.set_ylabel('Hours')
    ax.set_xlabel('Days')
    ax.set_title('Heatmap of crosswalk uses for all available days')

    fig.tight_layout()
    plt.savefig('/var/www/html/images/crosswalk_heatmap.png')

    return

def main(query, date):
    #generic image for overlaying
    #eventually take in name of file
    im_path = pathlib.Path('/var/www/html/images/image2.jpg')
    image = cv2.imread(str(im_path))
    master_copy = image.copy()
    #print(query)
    #print(str(im_path)) # MUST PRINT HERE OR ELSE WE DO NOT GET THE OUTPUT OF IMAGE PATH BACK INTO THE PHP FILE
    #draw lines using the database

    db_path = "./db/pedestrian_detections.db"
    db_connection = sqlite3.connect(db_path)
    db_cursor = db_connection.cursor()
    db_cursor.execute(str(query))
    record = db_cursor.fetchall() # [0] = perma id, [1] = xcoord, [2] = ycoord

    total_coords = []
    no_data = False
    #perma_id = record[0][0] # get first perma id for the day

    #print("something")

    #print(str(len(record)))

    if len(record) < 1 or record is None:  #if record is empty
        print("No data available")
        no_data = True
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

    if not no_data:
        pi_chart_per_hour(db_cursor, date)
        uses_per_hour(db_cursor, date) 

    print("What the hyuck")
    
    heatmap_per_hour(db_cursor, date)

    db_cursor.close()
    total_coords.clear()
#    cv2.putText(master_copy, "East", (500,120), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,0,255),6)
#    cv2.putText(master_copy, "West", (500,260), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,0,0),6)

    if os.path.exists("/var/www/html/images/user_img.jpg"):
        os.remove("/var/www/html/images/user_img.jpg")

    cv2.imwrite('/var/www/html/images/user_img.jpg', master_copy)
    db_connection.close()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
