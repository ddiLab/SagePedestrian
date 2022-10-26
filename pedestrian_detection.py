import os
import pathlib
import cv2
import numpy as np
from datetime import datetime
import xml.etree.ElementTree as ET
import sys
import getopt

sys.path.insert(1, './deep-person-reid/')
import torch
import torchreid
from torchreid.utils import FeatureExtractor
from collections import defaultdict, deque 
from recordtype import recordtype
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import sympy
import math

# CONTAINS MODEL - IF WANTING TO CHANGE MODELS CHANGE THE "model_name" variable
extractor = FeatureExtractor(model_name='osnet_x1_0', model_path='./model.pth.tar', device='cuda')

def load_crosswalk_corrdinates():
    import json
    try:
        with open('./crosswalk_coordinates.json') as xwalk:
            contents = xwalk.read()
            coordinates = json.loads(contents)
            return ( 
                coordinates["nroad_slope"], 
                coordinates["nroad_y_intercept"], 
                coordinates["sroad_slope"], 
                coordinates["sroad_y_intercept"], 
                np.array(coordinates["coordinates"])
            )
    except:
        print("File does not exist! Returning origin.")
        return 0, 0, 0, 0, np.array([[0,0], [0,0], [0,0], [0,0]])   #default

# Gets the crosswalk coordinates (the coordinates are slightly bigger than the exact coordinates from corner to corner)
def get_crosswalk_coordinates():
    coordinates = [[514, 796], [721, 783], [1095, 934], [763, 992]]
    return np.array(coordinates)

# Gets the exact crosswalk coordinates (used for highlighting later on in the script, not the actual detections)
def get_highlightable_coordinates():
    coordinates = [[524, 802], [667, 790], [1023, 941], [758, 962]] # for highlighting the crosswalk
    return np.array(coordinates)

# Parse the xml file
def parse_xml(xml_file):
    final_arr=[]
    tree= ET.parse(xml_file)
    root = tree.getroot()
    for object in root.findall('object'):
        arr=[]
        for box in object.find('bndbox'):
            if object.find('name').text == 'person':
                arr.append(int(box.text))
        if len(arr) > 0:
            final_arr.append(arr)
    return final_arr

# Multiple boxes per object, compresses into just one box for the object
# finds overlap between pictures, if there are no object boxes, skip the picture
def non_max_suppression_fast(boxes, overlapThresh):
#    print("NON MAX SUPRESSION FAST")
    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []
    # if the bounding boxes integers, convert them to floats --
    # this is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")
    # initialize the list of picked indexes 
    pick = []
    # grab the coordinates of the bounding boxes
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]
    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)
    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])
        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]
        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],
            np.where(overlap > overlapThresh)[0])))
    # return only the bounding boxes that were picked using the
    # integer data type
    return boxes[pick].astype("int")


def get_total_person_count(current_frame_persons):
    #global dict_person_assigned_number_frames
    try:
        return max(dict_person_assigned_number_frames) #key=dict_person_assigned_number_frames.get)   
    except:
        return 0  

#3
def update_current_frame_assignments(current_frame_persons, current_frame_sim_score,
                                     max_score, max_person_id, best_match_number, frame_queue):
#    print("UPDATE CURRENT FRAME ASSIGNMENTS")
#    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
#    print("max_Score=",max_score, "max_person_id= ", max_person_id, "previous_frame_match = ", best_match_number)
#    print("First if", current_frame_sim_score)
    if max_person_id in current_frame_sim_score:
        del current_frame_sim_score[max_person_id] 

#    print("Second", current_frame_sim_score)    
    if max_person_id == -1:
#        print(current_frame_sim_score)
        for current_id, current_person in enumerate(current_frame_persons):
#            print("current_frame_persons",current_person.assigned_number, current_person.person_id)
#             if current_person.person_id == current_person_id:
            if current_person.assigned_number == 0:                 #PROBLEM FOUND HERE
#                print(current_person.assigned_number, "CASE 1")
                current_frame_persons[current_id].assigned_number = get_total_person_count(
                    current_frame_persons)+1    #ADD 1 TO TOTAL PERSON COUNT BUT DOESN'T UPDATE TOTAL
#                print("New assigned number: ", current_person.assigned_number)
#                print(get_total_person_count(current_frame_persons))
                
#                print("Assigned number = ", current_frame_persons[current_id].assigned_number)
                if current_person.assigned_number in dict_person_assigned_number_frames:
                    dict_person_assigned_number_frames[current_frame_persons[current_id].assigned_number].append(current_person.frame_id)
#                    print("Key already exists")
                else:
                    dict_person_assigned_number_frames[current_frame_persons[current_id].assigned_number] = []
                    dict_person_assigned_number_frames[current_frame_persons[current_id].assigned_number].append(current_person.frame_id)
#                    print("Key was added to dict")
#                print(dict_person_assigned_number_frames)

#    print("Third", current_frame_sim_score)
    for current_id, current_person in enumerate(current_frame_persons):
        if current_person.person_id == max_person_id:
            within_range = True
            found = False
            #I will admit this is pretty bad
            for frame in frame_queue:
                for person in frame.person_records:
                    if person.assigned_number == best_match_number:
                        found = True
                        within_range = is_in_range(person.center_cords, current_person.center_cords)
                        break
                if found: break
#            print("Within range? ", within_range)
            if max_score > 0.6 and within_range:
#                print(current_frame_persons[current_id].assigned_number, "CASE 2")``
                current_frame_persons[current_id].assigned_number = best_match_number
#                print("Max score > 0.6, assigned number = ", best_match_number)
#                print("Current frame sim score: ", current_frame_sim_score)
                #if current_id in current_frame_sim_score.keys():
                    #if best_match_number in current_frame_sim_score[current_id].values():
                        #del current_frame_sim_score[current_id][best_match_number]
            else:
#                print(current_frame_persons[current_id].assigned_number, "CASE 3")
                current_frame_persons[current_id].assigned_number = get_total_person_count(current_frame_persons)+1
                if current_person.assigned_number in dict_person_assigned_number_frames:
                    dict_person_assigned_number_frames[current_person.assigned_number].append(current_person.frame_id)
                else:
                    dict_person_assigned_number_frames[current_person.assigned_number] = []
                    dict_person_assigned_number_frames[current_person.assigned_number].append(current_person.frame_id) 
#                print("Max score <= 0.6, assigned number = ", current_frame_persons[current_id].assigned_number)

#    print("Fourth", current_frame_sim_score)
    for person_id, scores in list(current_frame_sim_score.items()):
        for k, v in list(current_frame_sim_score[person_id].items()):
            if k == best_match_number:
#                print("Person ID: ", person_id)
#                print("Score: ", scores)
#                print("Match Found", k)
                del current_frame_sim_score[person_id][k]     

#    print("Fifth", current_frame_sim_score)
    return current_frame_persons,current_frame_sim_score

def is_all_current_frame_persons_assigned(current_frame_persons):
#    print("IS ALL CURRENT FRAME PERSONS ASSIGNED")
#    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    for current_id, current_person in enumerate(current_frame_persons):
        if current_person.assigned_number == 0:
 #           print(False)
            return False
#    print(True)
    return True

#2
def find_best_match_score(frame_queue, current_frame_persons, current_frame_sim_score,total_person_count):
#    print("FIND BEST MATCH SCORE")
#    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    while(not is_all_current_frame_persons_assigned(current_frame_persons)):
        max_score, max_score_person_id, best_match_number = 0, -1, -1
        for person_id, scores in list(current_frame_sim_score.items()):
            sim_score = current_frame_sim_score[person_id]
#            print("Pratool", person_id, sim_score)
            if len(sim_score) > 0 and max(sim_score.values()) > max_score:
                max_score = max(sim_score.values()) #get max value in sim_score -> sim_score is all similarity scores b/w person Id and other people
                max_score_person_id = person_id
                best_match_number = max(sim_score, key=sim_score.get)
#                print("Best match: " + str(best_match_number))
        current_frame_persons,current_frame_sim_score = update_current_frame_assignments(
            current_frame_persons, current_frame_sim_score, max_score, max_score_person_id, best_match_number, frame_queue)
    frame_queue, current_frame_persons = update_previous_frame(frame_queue, current_frame_persons)   
    #print("Current frame persons" + str(current_frame_persons)) 
    return current_frame_persons, frame_queue

#4, maybe this function could fix the same id in the same frame
def update_previous_frame(frame_queue, current_frame_persons):
    #print("UPDATE PREVIOUS FRAME")
    #print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    arr=[]
    for frame_id, previous_frame in enumerate(frame_queue):
        for person_id, previous_person in enumerate(previous_frame.person_records):
            found= False
            if previous_person.assigned_number in dict_person_assigned_number_frames:
                if len(dict_person_assigned_number_frames[previous_person.assigned_number]) == 1:
                    for current_person in current_frame_persons:
                        if current_person.assigned_number == previous_person.assigned_number:
                            found = True
                    if found is False:
                        arr.append([previous_person.assigned_number, frame_id, person_id])
    if len(arr)>0:
        for val in arr:
            del frame_queue[val[1]].person_records[val[2]]
        for person_id, current_person in enumerate(current_frame_persons):
            if current_person.assigned_number > val[0]:
                current_frame_persons[person_id].assigned_number -= len(arr)
    return frame_queue, current_frame_persons

#1
#CALLED FIRST
# returns things but never actually does anything with them              
def assign_numbers_to_person(frame_queue, current_frame_persons, total_person_count):
    #print("ASSIGN NUMBERS TO PERSON")
    #print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
    if not any(frame_queue): 
        #print("No frame queue:")
        for current_id, current_person in enumerate(current_frame_persons):
            #print("Current ID: " + str(current_id))
            total_person_count+=1
            current_frame_persons[current_id].assigned_number = total_person_count
        return current_frame_persons
    else:
        #print("Frame queue:")
        current_frame_sim_score=dict()
        for current_id, current_person in enumerate(current_frame_persons):            
            sim_score = defaultdict(list)
            #print("current person", current_person.person_id)
            for previous_frame in frame_queue:
                for previous_person in previous_frame.person_records:
                    similarity_score=cos(
                        current_person.feature,previous_person.feature).cpu().numpy()
                    sim_score[previous_person.assigned_number].append(similarity_score) #assigns a sim score to the prev person's assigned number
                    #print("Previous Frame", previous_person.assigned_number, previous_person.person_id )
                    #print("Frame id: ", previous_frame.frame_id)
                    #print("Sim score: " + str(similarity_score) + "\n")
            for assigned_number in sim_score:
                sim_score[assigned_number] = np.mean(sim_score[assigned_number])
            current_frame_sim_score[current_person.person_id] = sim_score  
            #print("Person Details", current_person.person_id, current_person.center_cords,sim_score)
        #print("Current frame sim score: ", current_frame_sim_score)
        #print("Call find best match score")
        return find_best_match_score(frame_queue, current_frame_persons, current_frame_sim_score, total_person_count)

#Adds the person position and the frame they're located in to the dictionaries
def update_person_position_and_frame(current_frame_persons,person_pos, current_frame_id):
    #print("UPDATE PERSON POSITION AND FRAME")
    #print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    #global dict_person_assigned_number_frames
    for current_person in current_frame_persons:
        if current_person.assigned_number not in person_pos:
            person_pos[current_person.assigned_number] = []
            person_pos[current_person.assigned_number].append(current_person.center_cords)
        else:
            person_pos[current_person.assigned_number].append(current_person.center_cords)
            
        if current_person.assigned_number in dict_person_assigned_number_frames:
            dict_person_assigned_number_frames[current_person.assigned_number].append(current_person.frame_id)
        else:
            dict_person_assigned_number_frames[current_person.assigned_number] = []
            dict_person_assigned_number_frames[current_person.assigned_number].append(current_person.frame_id)       
    #print("Person Pos: " + str(person_pos))    
    return person_pos


def update_person_frame(current_frame_id,frame_queue,person_pos,dict_person_crossed_the_road,dict_person_use_the_crosswalk):
    #print("UPDATE PERSON FRAME")
    #print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    #global dict_person_assigned_number_frames
    for assigned_number in list(dict_person_assigned_number_frames.keys()):
        arr = dict_person_assigned_number_frames[assigned_number]
        if len(arr) == 1:
            if current_frame_id - arr[0] > 0:
                #print(current_frame_id, arr,assigned_number )
                #print("CASE 1")
                delete_assigned_numbers_in_dicts(assigned_number, frame_queue, person_pos,
                                                 dict_person_crossed_the_road, dict_person_use_the_crosswalk)
        elif len(arr) == 2:
            if arr[1] - arr[0] > 1:
                #print("CASE 2")
                delete_assigned_numbers_in_dicts(assigned_number, frame_queue, person_pos, 
                                                 dict_person_crossed_the_road, dict_person_use_the_crosswalk)         
    # print(dict_person_assigned_number_frames)
    # print("Queue Length", len(frame_queue))
    # print("Frame Queue: " + str(frame_queue) + ", Person Pos: " + str(person_pos))
    return frame_queue,person_pos

def delete_assigned_numbers_in_dicts(assigned_number,frame_queue,person_pos,dict_person_crossed_the_road,dict_person_use_the_crosswalk):
    del dict_person_assigned_number_frames[assigned_number]
    if assigned_number in dict_person_crossed_the_road:
        del dict_person_crossed_the_road[assigned_number]
    if assigned_number in dict_person_use_the_crosswalk:
        del dict_person_use_the_crosswalk[assigned_number]
    if assigned_number in person_pos:
        del person_pos[assigned_number]
    for frame_id, previous_frame in enumerate(frame_queue):
        for person_id, previous_person in enumerate(previous_frame.person_records):
            if previous_person.assigned_number == assigned_number:
                del frame_queue[frame_id].person_records[person_id]   

def middle_between_points(point1, point2):
    middle = [None] * 2
    middle[0] = (point1[0] + point2[0]) // 2 #x coordinate
    middle[1] = (point1[1] + point2[1]) // 2 #y coordinate
    return middle

#checks if point1 and point2 are close to each other within a certain threshold
def is_in_range(point1, point2):
    MAX_DISTANCE = 650
    x_part = math.pow(point2[0] - point1[0], 2)
    y_part = math.pow(point2[1] - point1[1], 2)
    distance = math.sqrt(x_part + y_part)
    return distance < MAX_DISTANCE
        
# GLOBAL VARIABLES TO FIND LINES ON THE ROAD
# Slopes found using (y2-y1)/(x2-x1) - points found by looking at road, in standard form ax^2 + bx + c = 0
#north_road_slope = 0.037109375
#north_ycoord = 830
#south_road_slope = 0.0882352941176
#south_ycoord = 1025

def did_person_cross_the_road(assigned_number, person_pos):
    #print("DID PERSON CROSS THE ROAD")
    #print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    #crossing the road conditions
    north_side = False #condition_1
    south_side = False #condition_2
    #values for each side of the road, change these for new images

    #get crosswalk coords
    crosswalk_coords = xwalk_coords
    center_top = middle_between_points(crosswalk_coords[0], crosswalk_coords[1])
    center_bottom = middle_between_points(crosswalk_coords[2], crosswalk_coords[3])

    arr = []
    if assigned_number in person_pos:
        current_person_pos = person_pos[assigned_number]
        for cords in current_person_pos:
            #print(cords)
            if (north_road_slope*cords[0])+cords[1]-north_ycoord < 0: # use middle of road
                north_side = True
            if (south_road_slope*cords[0])+cords[1]-south_ycoord > 0:
                south_side = True
            if (north_road_slope*cords[0])+cords[1]-north_ycoord > 0 and (south_road_slope*cords[0])+cords[1]-south_ycoord < 0: #use middle of sidewalk
                arr.append(cords)
    if len(arr) > 0:
        distance_covered = float(Point(arr[0]).distance(Point(arr[-1])))
        total_distance = float(Point(center_top).distance(Point(center_bottom)))
        pct = distance_covered / total_distance
        #print ("assigned_number = ", assigned_number, "distance_covered = ", distance_covered, "total_distance = ",
              #total_distance, "pct = ", pct, "cords = ", arr[0], arr[-1])
        if (north_side and south_side) or (north_side and pct>0.8) or (south_side and pct>0.8):
            return True
    return False

def angle_between_crosswalk_and_trajectory(person_pos):
    #print("ANGLE BETWEEN CROSSWALK AND TRAJECTORY")
    #print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    import math
    #from sympy import Point, Line, pi

    #get crosswalk coords
    crosswalk_coords = xwalk_coords
    #get center of top of crosswalk
    center_top = middle_between_points(crosswalk_coords[0], crosswalk_coords[1])
    #get center of bottom
    center_bottom = middle_between_points(crosswalk_coords[2], crosswalk_coords[3])

    ne=sympy.Line(center_top,center_bottom)
    arr=[]
    angle=[]
    for cords in person_pos:
        if (north_road_slope*cords[0])+cords[1]-north_ycoord > 0 and (south_road_slope*cords[0])+cords[1]-south_ycoord < 0:
            arr.append(cords)
    for pair_id, val in enumerate(arr):
        if pair_id < len(arr)-1:
            angle.append(math.degrees(sympy.Line((arr[pair_id][0],arr[pair_id][1]), (arr[pair_id+1][0],arr[pair_id+1][1])).
                                  angle_between(ne)))
    # print(angle)
    return angle

#checks if person used crosswalk within a certain polygon
def did_person_use_the_crosswalk(person_cords, crosswalk_cords):
    #print("DID PERSON USE THE CROSSWALK")
    #print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    count=0
    # using the crosswalk coordinates
    crosswalk_polygon = Polygon(xwalk_coords)
    #print("Pratool person cords",person_cords)
    for cords in person_cords:
        if crosswalk_polygon.contains(Point(cords)):
            count+=1
    if count>2:
        return True
    return False

# img_original - The original image being processed (image)
# assigned_number - The person's assigned number (int)
# person_pos - Position of assigned_number (x,y pair)
# person_cords - Unused (x,y pair)
# crosswalk_cords - Coordinates of the crosswalk
# val - bounding box of person (x min,max y min, max)
# dict_person_crossed_the_road - Dictionary of people who crossed the road
# dict_person_use_the_crosswalk - Dictionary of people who used the crosswalk
def color_the_person_box(img_original, assigned_number, person_pos, person_cords, crosswalk_cords, 
                         val,dict_person_crossed_the_road, dict_person_use_the_crosswalk):
    #print("COLOR THE PERSON BOX")
    #print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    if did_person_cross_the_road(assigned_number, person_pos):
        #angle = angle_between_crosswalk_and_trajectory(person_pos[assigned_number])
        if assigned_number not in dict_person_crossed_the_road:
            dict_person_crossed_the_road[assigned_number] = True
           
        if did_person_use_the_crosswalk(person_cords, crosswalk_cords):# and any(x<25 or x>155 for x in angle):
            if assigned_number not in dict_person_use_the_crosswalk:
                dict_person_use_the_crosswalk[assigned_number] = True
              
            cv2.rectangle(img_original,(val[1],val[2]),(val[3],val[4]),(0,255,0),5)#green 
        else:
            cv2.rectangle(img_original,(val[1],val[2]),(val[3],val[4]),(0,0,255),5)#red
    else:
        cv2.rectangle(img_original,(val[1],val[2]),(val[3],val[4]),(255,255,255),3)#white
        
    #blur the rectangle
    x,y = val[1], val[2]
    w,h = val[3] - val[1], val[4] - val[2]
    roi = img_original[y:y+h, x:x+w]
    blur = cv2.GaussianBlur(roi, (17,17), 0) #ksize must be odd
    img_original[y:y+h, x:x+w] = blur

    return img_original, dict_person_crossed_the_road, dict_person_use_the_crosswalk

#For standalone use: All functionality of pedestrian detection script should remain intact,
#even when the script is done being modified to work in real time
def main(interval = -1, date = None, plot = False, initial=True):
    image_list=[]  # Array the holds the new images created from this script 
    date_arr=[]    # Main for loop array

    global dict_person_assigned_number_frames,dict_person_crossed_the_road,dict_person_use_the_crosswalk,dict_frame_time_stamp
    #crosswalk coordinates + lines
    global xwalk_coords, north_road_slope, north_ycoord, south_road_slope, south_ycoord

    max_second_count = 5
    second_count = 0
    person_id=1
    total_person_count=0
    frame_id=0
    frame_counter = 0
    frame_queue = deque([],6)              # Keeps track of previous 6 frames - used for re-id
    person_pos = dict()                    # Dictionary to hold coordinates of people
    dict_person_crossed_the_road = dict()  # Dictionary to check if the person has crossed the roads or not, person is key
    dict_person_use_the_crosswalk = dict() # Dictionary to check if the person has crossed the crosswalk or not, person is key
    dict_person_assigned_number_frames = dict() 
    dict_frame_time_stamp = dict()

    size = (0,0)    # Used in creating a .mp4 video at the end of the script

    frame_record = recordtype("frame_record", "frame_id person_records")
    person_record = recordtype("person_record", "person_id frame_id feature assigned_number center_cords bottom_cords")
    north_road_slope, north_ycoord, south_road_slope, south_ycoord, xwalk_coords = load_crosswalk_corrdinates()
    #print(north_road_slope, north_ycoord, south_road_slope, south_ycoord)
    pts = xwalk_coords# Uses exact crosswalk coordinates as a highlighter for visual aid

    hour_min = 13   #default hour range
    hour_max = 22
    emptyImage = False

    # Allows user to run the script through command line arguments (.xml files must exist)
    if len(sys.argv)-1 == 0 and interval == -1:
        print("\n \nFormat: python pedestrian_detection.py -s [hour_min] -e [hour_max] -d [date1, date2, ...]")
        print("     -s: Hour interval start")
        print("     -e: Hour interval end")
        print("     -d: List of dates that you want to run. Format: yyyy/mm/dd (Must go at end)")
        print("     Default hours are 13 (8am) to 22 (5pm)")
        return

    if interval != -1 and date != None: #called from obj detection
        #hour_min = 13                   #we are running the whole day through obj detection
        #hour_max = 22
        date_arr.append(date)
    else:                               #standalone with params
        opts, args = getopt.getopt(sys.argv[1:], "s:e:d:")
        has_day = False

        for opt, arg in opts:
            if opt in ['-s']: hour_min = int(arg)
            elif opt in ['-e']: hour_max = int(arg)
            elif opt in ['-d']: 
                has_day = True
                date_arr.append(arg)
                for date in args:   #append any extra days.
                    date_arr.append(date)

    # Driver loop - based off of the days the user has entered as a CMD line argument
    for day in date_arr:
        PATH_TO_IMAGES_DIR = pathlib.Path('/raid/AoT/sage/000048B02D15BC7D/bottom/'+ day + '/')
        TEST_RAW_IMAGE_PATHS = sorted(list(PATH_TO_IMAGES_DIR.rglob("*.jpg")))
        
        if len(TEST_RAW_IMAGE_PATHS) < 1:
            print("No images found.")
            return

        # Nested loop - checks each .jpg image in the sage directory
        for im in TEST_RAW_IMAGE_PATHS:
            try:
                # Get the name of the .jpg file and strip the unneccesary mumbo jumbo
                file_name = os.path.basename(im)
                var_date_time = file_name[:len(file_name)-4].split("T")
                var_date_str, var_time_str = var_date_time[0], var_date_time[1]
                var_time_str = var_time_str.replace('+0000','')
                var_date_object = datetime.strptime(var_date_str + " " + var_time_str, "%Y-%m-%d %H:%M:%S")
                formatted = "-".join(["{:02d}".format(var_date_object.month), "{:02d}".format(var_date_object.day), str(var_date_object.year)])
                file_name = file_name.replace('.jpg','')
                # Checking for valid hours we use
                if hour_min <= var_date_object.hour <= hour_max: 
                    xml_file = "/raid/AoT/image_label_xmls/" + formatted + "/"+file_name+".xml"
                    print(xml_file)
                    if not os.path.isdir('/raid/AoT/image_label_xmls/crosswalk_detections/' + var_date_str): # adds day to directory
                        os.mkdir('/raid/AoT/image_label_xmls/crosswalk_detections/' + var_date_str)
                    if os.path.exists(xml_file):
                        frame_id+=1
                        frame_rec = frame_record(0,0)
                        frame_rec.frame_id = frame_id
                        #print("Frame id", frame_id )
                        current_frame_persons=[]
                        
                        person_coordinates = parse_xml(xml_file)                                        # get the coordinates for a person in the picture
                        person_coordinates = non_max_suppression_fast(np.array(person_coordinates),0.3) # Supress extra boxes around objects

                        # Check to see if a person is actually in the image 
                        if len(person_coordinates)>0:
                            count = 0
                            second_count = 0
                            #print("Printing person coordinates: ", person_coordinates)
                            img_original = cv2.imread(str(im))   # img_original now holds the image
                            img_c = img_original.copy()          # a copy of the original
                            temp_arr=[]
                            # person : xmin, xmax, ymin, ymax of person                          
                            for person in person_coordinates:
                                frame_counter += 1
                                if abs((person[1]-person[3]) * (person[0]-person[2])) > 1750: # check to see if below 1700 y line, bounding box size > 1750
                                    # for increased accuracy can do Person[0] > 1900, ignores right half of screen which can cause massive re-id errors
                                    if frame_id not in dict_frame_time_stamp:
                                        dict_frame_time_stamp[frame_id] = var_date_time
                                    #print("Person: ", person , " - end person print")
                                    img = img_original[person[1]:person[3], person[0]:person[2]]
            #                         print((person[1]-person[3]) * (person[0]-person[2]))
            #                         print("Index = ", count, "Image Shape = ",img.shape)
                                    person_rec = person_record(0,-1,0,0,0,0)
                                    person_rec.person_id = person_id
                                    person_rec.frame_id = frame_rec.frame_id 
            #                         print(np.average([person[0],person[2]]))
                                    #print("xml file",xml_file) # Debugging purposes
                                    person_rec.center_cords = [int(np.average([person[0],person[2]])), person[3]] # finds the center of the bounding box
                                    #print("center coords: ", person_rec.center_cords)
                                    person_rec.feature = extractor(img)
                                    #print("Printing person_rec.feature: ")
                                    #print(person_rec.feature)
                                    #print("end person rec feature")
                        
            #                         print(person_id, person)
                                    
                                    current_frame_persons.append(person_rec)
                                    
                                    temp_arr.append([person_id, person[0],person[1], person[2], person[3]])
                                    #print("Temp arr: " + str(temp_arr))
                                    
                                    person_id+=1
                                else: 
                                    if len(frame_queue) > 0 and frame_counter % 5 == 0 and frame_counter != 0:
                                        frame_queue.popleft()
                                        frame_counter = 0

            #                 frame_queue, person_pos=update_person_frame(frame_id,frame_queue, person_pos)        
                            assign_numbers_to_person(frame_queue, current_frame_persons, total_person_count)
                            
                            person_pos = update_person_position_and_frame(current_frame_persons, person_pos, frame_rec.frame_id)
            #                 print(person_pos)
                            frame_queue, person_pos = update_person_frame(frame_id,frame_queue, person_pos, 
                                                                            dict_person_crossed_the_road,
                                                                            dict_person_use_the_crosswalk)
                            total_person_count = get_total_person_count(current_frame_persons)
                            
                            for curr_person in current_frame_persons:
                                #print("Person id: " + str(curr_person.person_id))
                                person_cross_the_road = did_person_cross_the_road(curr_person.assigned_number,person_pos)
                                #print("Current person", person_cross_the_road)
                                if person_cross_the_road:
                                    print(curr_person.assigned_number, 
                                        did_person_use_the_crosswalk(person_pos[curr_person.assigned_number], pts))               
                            # fills the crosswalk GREEN
                            cv2.fillPoly(img_original, pts = [pts], color=(0,255,0))
                            # draw lines that people will be checked for crossing - RED
                            cv2.line(img_original,(0,830),(2560,735),(0,0,255),8)
                            cv2.line(img_original,(0,1025),(2550,800),(0,0,255),8)
                            # give transparency to the crosswalk and road lines
                            img_new = cv2.addWeighted(img_c, 0.3, img_original, 1 - 0.3, 0)

                            frame_rec.person_records = current_frame_persons
                            frame_queue.append(frame_rec)
                            #print("Total person count", total_person_count)
                            for val in temp_arr:
                                for p_id, p_val in enumerate(current_frame_persons):
                                    if current_frame_persons[p_id].person_id == val[0]:
                                        img_new, dict_person_crossed_the_road, dict_person_use_the_crosswalk = color_the_person_box(img_new, 
                                                             current_frame_persons[p_id].assigned_number, 
                                                             person_pos, 
                                                             person_pos[current_frame_persons[p_id].assigned_number], 
                                                             pts,
                                                             val,
                                                             dict_person_crossed_the_road,
                                                             dict_person_use_the_crosswalk)
                                        # Write the assigned number onto the image next to the person - IN BLUE
                                        cv2.putText(img_new, str(current_frame_persons[p_id].assigned_number), (val[1],val[2]-30), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,255), 5)

                            # Writing onto the image original person count, person used road or crosswalk stated - NOT weighted
                            cv2.putText(img_new, "Person count = "+ str(total_person_count), (
                                                50, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,255,239), 6)
                            cv2.putText(img_new, "Person crossed road = "+ str(len(dict_person_crossed_the_road)), (
                                                50, 260), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,255,239), 6)  
                            cv2.putText(img_new, "Person used crosswalk = "+ str(len(dict_person_use_the_crosswalk)), (
                                                50, 400), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,255,239), 6)   

                            image_date = str(var_date_object).replace("00:00:00","")
                            image_date = image_date
                            cv2.putText(img_new, str(image_date)  , (50,1730), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,255,239),6)

                            # used for video writer
                            height, width, layers = img_new.shape
                            size = (width,height)
                            image_list.append(img_new)
                            # Saves file with writing to the path - ALL .JPGS NOW STORED IN CROSSWALK DETECTIONS
                            cv2.imwrite('/raid/AoT/image_label_xmls/crosswalk_detections/' + var_date_str + "/" + file_name + ".jpg", img_new)
                            #print("\n\n") 
                        else:   #no person in the image
                            if not emptyImage: 
                                cv2.imwrite('/raid/AoT/image_label_xmls/crosswalk_detections/' + var_date_str + "/empty_image.jpg", cv2.imread(str(im)))
                                emptyImage = True
                            second_count += 1
                            frame_queue, person_pos =update_person_frame(frame_id,frame_queue, person_pos, 
                                                                            dict_person_crossed_the_road,
                                                                            dict_person_use_the_crosswalk)
                            if len(frame_queue) > 0 and second_count > max_second_count: #wait at least 5 seconds before popping
                                frame_queue.popleft() #should remove old data from queue over large time gaps
            except Exception as e:
                print("Exception thrown:", str(e))
                continue

    #DATABASE PORTION BELOW
    plot = True    # for db connection testing short periods of time
    if plot: #plot is set to true or false from plot_object_detection.py depending on the hour has changed or not
        import server_info
        
        connection = server_info.connect_to_database()
        
        #can't connect to db
        if connection is None:
            print("Could not connect to database.")
            return
        
        cursor = connection.cursor(buffered = True, dictionary = True)

        latest_id = 0                   #get most recent id in data
        cursor.execute(f"SELECT PERMAID FROM Person ORDER BY PERMAID DESC LIMIT 1;")
        result = cursor.fetchone()

        if result is not None:
            new_id = result["PERMAID"]
            if new_id is not None:
                latest_id = new_id
                print("Latest ID ", latest_id)
            else:
                print("Database empty")     #temporary

        #check if day exists.
        #if it does, we want to remove any data associated with it before inserting into db

        #Insert values into Frame, we probably don't want to insert new people
        #if frame time already exists
        for key, value in dict_frame_time_stamp.items():
            new_date = value[0] + "T" + value[1].replace('+0000','')
            path = "/raid/AoT/image_label_xmls/crosswalk_detections/" + var_date_str + "/" + new_date + "+0000.jpg"
            cursor.execute("INSERT INTO Frame (DATE, PATH, FRAMEID) VALUES (%s,%s,%s)", (str(new_date), str(path), int(key)))

        try:
            #insert values into person
            for key, value in person_pos.items():
                road = 1 if key in dict_person_crossed_the_road else 0       #set road and crosswalk flags in the cords csv file
                crosswalk = 1 if key in dict_person_use_the_crosswalk else 0
                east = 0 if (value[0][1] - value[-1][1] >= 0) else 1
                north = 1 if (value[0][0] - value[-1][0] < 0) else 0
                cursor.execute("INSERT INTO Person (PERMAID, DAYID, USECROSSWALK, USEROAD, NS, EW) VALUES (%s,%s,%s,%s,%s,%s)", (int(latest_id+key), key, crosswalk, road, north, east))
        except:
            print("Primary key probably exists.")

        try:
            #insert values into Coordinate and Contains tables.
            for key, frame_id_array in dict_person_assigned_number_frames.items():
                for i in range(1, len(frame_id_array)): #frame_id in frame_id_array: #loop through each frame
                    frame_id = frame_id_array[i]        #use indicies to skip first frame in dictionary. CSV File has extra frame at start, but person_cords csv has # of frames - 1
                    coord = person_pos[key][i-1]        #get the coordinates of the current frame in array
                    timestamp = ('T'.join(dict_frame_time_stamp[frame_id])) #get timestamp using current frame id
                    timestamp = str(timestamp.replace('+0000', ''))
                    cursor.execute("INSERT INTO Coordinate (PERMAID, DATE, XCOORD, YCOORD) VALUES (%s,%s,%s,%s)",
                                    (int(latest_id+key), timestamp, int(coord[0]), int(coord[1]) ))
                    cursor.execute("INSERT INTO Contains (PERMAID, DATE) VALUES (%s,%s)", (int(latest_id+key), timestamp) )
        except:
            print("Primary key????")

        #commit changes to database
        connection.commit()
        #close connection to database
        connection.close()

if __name__ == '__main__':
    main()
