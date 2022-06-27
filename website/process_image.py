from audioop import cross
import pathlib
import cv2
from shutil import copyfile
from datetime import datetime
import time
import sqlite3
import os
import numpy as np
import math
import mysql.connector as mariadb

import sys
sys.path.insert(0, '/home/wesley/')
import server_info

def pi_chart_per_hour(db_cursor, date):
    from matplotlib import pyplot as pie
    #crosswalk uses per hour for sepcific 'date'
    query2 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%H') as hour from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains where DATE like '" + date + "%') group by hour;"
    #total number of crosswalk uses for 1 day
    db_cursor.execute(query2)
    results = db_cursor.fetchall()
    pie_labels = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    #format results
    hourly_xwalk_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for row in results:
        hourly_xwalk_data[int(row[1]) - pie_labels[0]] = row[0]

    data = np.array(hourly_xwalk_data, dtype=int)

    pie_labels = ["8am", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm"]
    
    fig,ax = pie.subplots()
    #print(hourly_xwalk_data)
    ax.pie(data, labels = pie_labels)
    title='Crosswalk usages per hour for ' + str(date)
    ax.set(aspect="equal", title=title)
    fig.savefig('./images/xwalk_pie_per_hr.png')

    pie.close(fig)

    return

def uses_per_hour(db_cursor, date):
    from matplotlib import pyplot as plt
    query2 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%H') as hour from Contains where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select distinct PERMAID from Contains where DATE like \'" + date + "%\') group by hour;"
    db_cursor.execute(query2)
    road_results = db_cursor.fetchall()
    query3 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%H') as hour from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains where DATE like \'" + date + "%\') group by hour;"
    db_cursor.execute(query3)
    cwalk_results = db_cursor.fetchall()
    #format results
    hours = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22] #use internal hours
    hourly_cwalk_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    hourly_road_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for res in cwalk_results:
        hourly_cwalk_data[int(res[1]) - hours[0]] = res[0]
    for res in road_results:
        hourly_road_data[int(res[1]) - hours[0]] = res[0]

    hours = ['8am', '9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm']

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
    fig.savefig('./images/uses_per_hour.png')
    
    plt.close(fig)

    return

def heatmap_per_hour(db_cursor, date):
    from matplotlib import pyplot as plt
    query2 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d') as day, DATE_FORMAT(DATE, '%H') as hour from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains) group by hour,day order by day;"
    db_cursor.execute(query2)
    heatmap_raw = db_cursor.fetchall()
    #format results    
    counts = []
    hours = [22, 21, 20, 19, 18, 17, 16, 15, 14, 13]

    for i in range(0, len(hours), 1):
        counts.append([])
    days = []

    sub_hours = []
    last_day = None

    for result in heatmap_raw:
        if result[1] not in days:
            days.append(result[1])
        
        if last_day != result[1] and last_day != None:    #day changed or last day
            for i in range(hours[0], hours[-1]-1, -1):
                if i not in sub_hours:
                    counts[hours[0]-i].append(0)
            sub_hours = []

        sub_hours.append(int(result[2]))

        last_day = result[1]
        counts[hours[0] - int(result[2])].append(result[0])

    for i in range(hours[0], hours[-1]-1, -1):  #finish append 0s based on the last day
        if i not in sub_hours:
            counts[hours[0]-i].append(0)

    #reformat hours to be more readable
    for i in range(0, len(hours), 1):
        hour = hours[i]
        suffix = "am"
        if hour >= 17:
            suffix = "pm"
        if hour == 17:
            hours[i] = hour - 5
        else:
            hours[i] = (hours[i] - 5) % 12
        hours[i] = str(hours[i]) + suffix
    
    data = np.array(counts, dtype=int)

    fig, ax = plt.subplots()
    ax.set_xticks(np.arange(len(days)), days)
    ax.set_yticks(np.arange(len(hours)), hours)

    im = ax.imshow(data)

    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Frequency", rotation=-90, va="bottom")

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    ax.set_ylabel('Hours')
    ax.set_xlabel('Days')
    ax.set_title('Crosswalk uses for all available days')

    fig.tight_layout()
    fig.savefig('./images/crosswalk_heatmap.png')

    plt.close(fig)

    return

def create_line_chart(db_cursor, date):
    from matplotlib import pyplot as plt
    query2 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d') as day from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains) group by day order by day;"
    hours = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    days = []
    counts = []
    days = []

    db_cursor.execute(query2)
    line_graph_raw = db_cursor.fetchall()

    for res in line_graph_raw:
        counts.append(int(res[0]))
        days.append(res[1])

    fig, ax = plt.subplots()

    ax.set_xticks(np.arange(len(days)), days)
    ax.set_xticklabels(days,rotation=65)
    ax.set_title("Crosswalk Uses Per Day For All Days")
    ax.set_xlabel("Days")
    ax.set_ylabel("Crosswalk Uses")
    ax.plot(days, counts)
    fig.tight_layout()

    fig.savefig('./images/crosswalk_line_chart.png')
    
    plt.close(fig)

    return

def main(query, date):
    #generic image for overlaying
    #eventually take in name of file
    im_path = pathlib.Path('./images/image2.jpg')
    image = cv2.imread(str(im_path))
    master_copy = image.copy()
    #draw lines using the database

    """
    db_path = "./db/pedestrian_detections.db"
    db_connection = sqlite3.connect(db_path)
    db_cursor = db_connection.cursor()
    db_cursor.execute(str(query))
    """
    connection = server_info.connect_to_database()
    db_cursor = connection.cursor()
    db_cursor.execute(str(query))

    record = db_cursor.fetchall() # [0] = perma id, [1] = xcoord, [2] = ycoord
    #print(record)
    total_coords = []
    no_data = False

    #for r in record:
        #print(r)

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
        heatmap_per_hour(db_cursor, date)
        create_line_chart(db_cursor, date)  

    db_cursor.close()
    total_coords.clear()
#    cv2.putText(master_copy, "East", (500,120), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,0,255),6)
#    cv2.putText(master_copy, "West", (500,260), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,0,0),6)

    if os.path.exists("./images/user_img.jpg"):
        os.remove("./images/user_img.jpg")

    cv2.imwrite('./images/user_img.jpg', master_copy)
    connection.close()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
