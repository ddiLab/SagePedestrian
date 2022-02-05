import pathlib
import cv2
import numpy as np
from shutil import copyfile
from datetime import datetime
import time

def draw_lines(date):
    import csv
    #generic image for overlaying
    #eventually take in name of file
    im_path = pathlib.Path('/raid/AoT/sage/000048B02D15BC7D/bottom/2021/09/02/17/2021-09-02T17:00:00+0000.jpg')
    image = cv2.imread(str(im_path))
    image_copy = image.copy()

    #get file paths
    cords_path = "/raid/AoT/image_label_xmls/crosswalk_detections/" + date + "/person_cords.csv"
    timestamp_path = "/raid/AoT/image_label_xmls/crosswalk_detections/" + date + "/frame_timestamps.csv"
    person_frames_path = "/raid/AoT/image_label_xmls/crosswalk_detections/" + date + "/person_frames.csv"
    hour = 13 #probably better to grab the inital hour from the file but this works for now
    person_id = 0
    found = False

    #open coordinates file
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
    return

def strip_characters(data):
    data = data.replace('[', '')
    data = data.replace(']', '')
    data = data.replace(' ', '')
    return data

# for using the script without pedestrian_detection.py
if __name__ == '__main__':
    draw_lines("2021-08-31")
