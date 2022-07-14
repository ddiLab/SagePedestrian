from audioop import cross
import pathlib
import cv2
from shutil import copyfile
from datetime import datetime
from datetime import date
from datetime import timedelta
import time
import os
import numpy as np
import math
import mysql.connector as mariadb
import sys
import json
from SageBokeh import bokeh_heat_map

sys.path.insert(0, '/home/wesley/')
import server_info

def heatmap_per_hour(db_cursor):
    from matplotlib import pyplot as plt
    query2 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day, DATE_FORMAT(DATE, '%H') as hour from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains) group by hour,day order by day;"
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
        current_date = datetime.strptime(result[1], '%Y-%m-%d %a')

        while last_day != None and (current_date - last_day).days > 1:
            last_day = last_day + timedelta(days=1)
            days.append(last_day.strftime('%Y-%m-%d %a'))
            for i in range(hours[0], hours[-1]-1, -1):
                counts[hours[0]-i].append(0)
        
        date = current_date.strftime('%Y-%m-%d %a')
        if date not in days:
            days.append(date)

        if last_day != current_date and last_day != None:    #day changed or last day
            for i in range(hours[0], hours[-1]-1, -1):
                if i not in sub_hours:
                    counts[hours[0]-i].append(0)
            sub_hours = []

        sub_hours.append(int(result[2]))

        last_day = current_date
        counts[hours[0] - int(result[2])].append(result[0])

    for i in range(hours[0], hours[-1]-1, -1):  #finish append 0s based on the last day
        if i not in sub_hours:
            counts[hours[0]-i].append(0)

    #for row in counts:
        #print(row)

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
    max_count = np.max(data)

    fig, ax = plt.subplots()
    ax.set_xticks(np.arange(len(days)), days)
    ax.set_yticks(np.arange(len(hours)), hours)

    im = ax.imshow(data)

    cbar = ax.figure.colorbar(im, ax=ax, ticks=[0, max_count/2, max_count])
    cbar.ax.set_ylabel("Frequency", rotation=-90, va="bottom")
    cbar.ax.set_yticklabels(['Low', 'Medium', 'High'])

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    ax.set_ylabel('Hours')
    ax.set_xlabel('Days')
    ax.set_title('Crosswalk uses for all available days')

    fig.tight_layout()
    fig.savefig('./images/crosswalk_heatmap.png')

    plt.close(fig)

    return

def create_line_chart(db_cursor):
    from matplotlib import pyplot as plt
    crosswalk_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains) group by day order by day;"
    road_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select distinct PERMAID from Contains) group by day order by day;"

    days = []
    xwalk_counts = []
    road_counts = []
    days = []

    db_cursor.execute(crosswalk_query)
    line_graph_raw = db_cursor.fetchall()

    last_date = None
    for res in line_graph_raw:
        current_date = datetime.strptime(res[1], '%Y-%m-%d %a')
        while last_date != None and (current_date - last_date).days > 1:
            last_date = last_date + timedelta(days=1)
            xwalk_counts.append(0)
            days.append(last_date.strftime('%Y-%m-%d %a'))
        xwalk_counts.append(int(res[0]))
        days.append(res[1])
        last_date = current_date

    db_cursor.execute(road_query)
    road_raw = db_cursor.fetchall()

    for res in road_raw:
        current_date = datetime.strptime(res[1], '%Y-%m-%d %a')
        for i in range((current_date-last_date).days-1):
            road_counts.append(0)
        last_date = current_date
        road_counts.append(int(res[0]))

    fig, ax = plt.subplots()

    ax.set_xticks(np.arange(len(days)), days)
    #ax.set_xticklabels(days,rotation=80)
    ax.set_title("Road/Crosswalk Uses Per Day For All Days")
    ax.set_xlabel("Days")
    ax.set_ylabel("Uses")
    ax.scatter(x=days, y=xwalk_counts, label="Crosswalk")
    ax.scatter(x=days, y=road_counts, label="Road")
    #ax.plot(days, xwalk_counts, label="Crosswalk")
    #ax.plot(days, road_counts, label="Road")
    ax.legend()

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    fig.tight_layout()

    fig.savefig('./images/crosswalk_line_chart.png')
    
    plt.close(fig)

# THIS SCRIPT IS AUTOMATED USING CRONJOB TO RUN EVERY DAY AT 12:00AM
def last24():
    today = date.today()
    non_string_yesterday = today - timedelta(days = 1)
    yesterday = str(non_string_yesterday)
    yesterday = yesterday.replace("/","-")
    #print(yesterday)
    query = "SELECT PERMAID, XCOORD, YCOORD FROM Coordinate WHERE DATE LIKE '" + yesterday + "%';"
    #print(query)

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

    path_dict = {}

    if len(record) < 1 or record is None:  #if record is empty
        print("None")
        no_data = True
    else:
        perma_id = record[0][0]
        for row in record:
            if(row[0] != perma_id):
                perma_id = row[0]
                #if(total_coords[0][1] > 1200):
                    #master_color = (255,0,0)
                #else:
                    #master_color = (0,0,255)
                #master_copy = cv2.polylines(master_copy, np.int32([total_coords]), False, master_color)
                total_coords.clear()
                coordinate = (row[1],row[2])
                total_coords.append(coordinate)
            else:
                coordinate = (row[1],row[2]) # tuple of the rows coordinates
                total_coords.append(coordinate)
                if perma_id not in path_dict:
                    path_dict[perma_id] = []
                path_dict[perma_id].append(coordinate)

    #heatmap_per_hour(db_cursor)
    create_line_chart(db_cursor)
    print(json.dumps(path_dict)) #print the path dictionary so php can retrieve it
    bokeh_heat_map(db_cursor)

    db_cursor.close()

    #if os.path.exists("./images/homepage.jpg"):
        #os.remove("./images/homepage.jpg")

    #cv2.imwrite('./images/homepage.jpg', master_copy)
    connection.close()
    #print("Trajectories traced for yesterday")

if __name__ == '__main__':
    last24()
