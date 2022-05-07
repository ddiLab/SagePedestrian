import pathlib
import cv2
import numpy as np
from shutil import copyfile
from datetime import datetime
import time
import sqlite3

#code isn't the most efficient at the moment
#Some improvements: Do the hourly and master plots at the same time
#                   Only pull information from the database once
def draw_lines(date):
    import csv
    #date format: Yyyy-Mm-Dd
    #strip date
    var_date_object = datetime.strptime(date, "%Y-%m-%d") # for individual hour printing
    print(var_date_object)
    master_date_object = str(var_date_object)
    master_date_object = master_date_object.replace(' 00:00:00','') # for keeping track of each day passing through for all line image
    formatted = str(var_date_object.year) + "/" +  "{:02d}".format(var_date_object.month) + "/" + "{:02d}".format(var_date_object.day) + "/13/"

    #generic image for overlaying
    #eventually take in name of file
    im_path = pathlib.Path('/raid/AoT/sage/000048B02D15BC7D/bottom/' + formatted + date + 'T13:00:00+0000.jpg')
    image = cv2.imread(str(im_path))
    image_copy = image.copy()
    master_copy = image.copy()

    #get file paths
    cords_path = "/raid/AoT/image_label_xmls/crosswalk_detections/" + date + "/person_cords.csv"
    timestamp_path = "/raid/AoT/image_label_xmls/crosswalk_detections/" + date + "/frame_timestamps.csv"
    person_frames_path = "/raid/AoT/image_label_xmls/crosswalk_detections/" + date + "/person_frames.csv"
    hour = 13 #probably better to grab the inital hour from the file but this works for now
    person_id = 0
    found = False

    #draw lines using csv files
    """
    with open(cords_path, 'r', newline='') as a, open(timestamp_path, 'r', newline='') as b, open(person_frames_path, 'r', newline='') as c:
        #read in every file with csv reader
        cords = csv.reader(a)
        timestamps = csv.reader(b)
        people = csv.reader(c) # maybe rename to generic names for other models (entities?)

        #get all coordinates
        coordinates = []
        for line in cords:
            data = line[1]
            data = strip_characters(data)
            cord = data.split(",")
            xy_pairs = []

            #get xy pairs
            for i in range(0, len(cord)-1, 2):
                pair = [cord[i], cord[i+1]]
                xy_pairs.append(pair)

            coordinates.append(np.array(xy_pairs))


        get_next = True


        #look at every timestamp
        for line in timestamps:
            #strip hour and id
            frame_id = line[0]
            timestamp = datetime.strptime(line[1], "['%Y-%m-%d', '%H:%M:%S+0000']")
            timestamp = timestamp.time()

            # condition to check after the first loop thru, sets hours for images
            if(hour != timestamp.hour): # not used until second time + through script
                cv2.imwrite('/raid/AoT/image_label_xmls/crosswalk_detections/' + date + '/line_result_H' + str(hour) + '.jpg', image)
                image = cv2.imread(str(im_path))# read in fresh image to put cords on
                image_copy = image.copy()       # make a copy that will have the actual coordinates drawn on

            hour = timestamp.hour
            found = True # for finding the frame id within the persons known frames

            # only want to grab first person
            if get_next is True:
                # next() returns the next element 
                person = next(people, None)
                get_next = False
            # while we have a frame within the person_frames array
            while(found and person is not None):
                split = strip_characters(person[1])
                result = split.rsplit(",")
                print("Got next person")
                print("ID: " + str(frame_id) + ", result: " + str(result))
                if frame_id in result:
                    print("Found frame ID")
                    if int(person[0]) < len(coordinates):
                        line = coordinates[int(person[0])]
                        print("Got next line")
                        #update color
                        if int(coordinates[int(person[0])][0][1]) > 1200: color = (255, 0, 0)
                        else: color = (0, 0, 255)            

                        print(str(coordinates[int(person[0])]))

                        image_copy = cv2.polylines(image_copy, np.int32([coordinates[int(person[0])]]), False, color) # draw
                        image = cv2.addWeighted(image_copy, 0.3, image, 1 - 0.3, 0) # combine the coordinates drawn on image copy onto the image original
                        cv2.putText(image, "Towards Camera", (500,120), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,0,255),6)
                        cv2.putText(image, "Away from Camera", (500,260), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,0,0),6)
                        cv2.putText(image, "Hour: " + str(hour), (500,400), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,255,0),6)
                    person = next(people, None) # iterate to the next person 
                else:
                    found = False   
        cv2.imwrite('/raid/AoT/image_label_xmls/crosswalk_detections/' + date + '/line_result_H' + str(hour) + '.jpg', image) # writes hour 13 
    a.close()
    b.close()
    c.close()
    """

    #draw lines using the database
    db_path = "/raid/AoT/image_label_xmls/crosswalk_detections/pedestrian_detections.db"
    db_connection = sqlite3.connect(db_path)
    db_cursor = db_connection.cursor()
    master_date = master_date_object + '%'
    db_cursor.execute("SELECT PERMAID,XCOORD,YCOORD FROM Coordinate WHERE DATE LIKE ?;", (master_date,))
    record = db_cursor.fetchall() # [0] = perma id, [1] = xcoord, [2] = ycoord
    
    if len(record) < 1:  #if record is empty
        print("No records found")
        return  #just exit

    total_coords = []
    perma_id = record[0][0] # get first perma id for the day

    #hourly images
    for i in range(13, 23):
        date_hour = master_date_object + 'T' + str(i) + '%'
        print("Date: ", date_hour)
        db_cursor.execute("SELECT PERMAID,XCOORD,YCOORD FROM Coordinate WHERE DATE LIKE ?;" ,(date_hour,))
        rec = db_cursor.fetchall() # [0] = perma id, [1] = xcoord, [2] = ycoord
        image_copy = image.copy()   #create a copy for the specific hour
        print("Length: ", len(rec))
        id = rec[0][0]
        for row in rec:
            if(id != row[0]):   #if the ids are different, update colors and write to image
                #update color
                if(total_coords[0][1] > 1200):  master_color = (255,0,0)
                else: master_color = (0,0,255)

                image_copy = cv2.polylines(image_copy, np.int32([total_coords]), False, master_color)
                total_coords.clear()    #clear coords for single person
                coordinate = (row[1],row[2])
                total_coords.append(coordinate)
                id = row[0] #reset the current ID
            else:
                coordinate = (row[1],row[2]) # tuple of the rows coordinates
                total_coords.append(coordinate)

        #write hourly images
        total_coords.clear() # end of record read in
        cv2.putText(image_copy, "Towards Camera", (500,120), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,0,255),6)
        cv2.putText(image_copy, "Away from Camera", (500,260), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,0,0),6)
        cv2.putText(image_copy, "Hour: " + str(i), (500,400), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 0), 6)
        cv2.imwrite('/raid/AoT/image_label_xmls/crosswalk_detections/' + date + '/line_result_' + str(i) + '.jpg', image_copy)
        

    #track permaid, store tuples in list, loop thru list, for master image containing all points
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

    total_coords.clear() # end of record read in

    cv2.putText(master_copy, "Towards Camera", (500,120), cv2.FONT_HERSHEY_SIMPLEX, 4, (0,0,255),6)
    cv2.putText(master_copy, "Away from Camera", (500,260), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,0,0),6)
    cv2.imwrite('/raid/AoT/image_label_xmls/crosswalk_detections/' + date + '/line_result_M' + '.jpg', master_copy)

    db_connection.close()   #close db
    return

def strip_characters(data):
    data = data.replace('[', '')
    data = data.replace(']', '')
    data = data.replace(' ', '')
    return data

# for using the script without pedestrian_detection.py
if __name__ == '__main__':
    draw_lines("2022-05-03")
