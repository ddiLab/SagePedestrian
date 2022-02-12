import os
import pathlib
import cv2
import numpy as np
import operator
from datetime import datetime
from shutil import copyfile
import xml.etree.ElementTree as ET
import sys
import matplotlib
import math
from matplotlib import pyplot as plt
from numpy.core.fromnumeric import var

sys.path.insert(1, '../deep-person-reid/')
import torch
import torchreid
from torchreid.utils import FeatureExtractor
from collections import defaultdict, deque 
from recordtype import recordtype
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import sympy
import pickle
import time

# CONTAINS MODEL - IF WANTING TO CHANGE MODELS CHANGE THE "model_name" variable
extractor = FeatureExtractor(model_name='osnet_x1_0', model_path='./model.pth.tar', device='cuda')


# Uses crosswalk coordinates from xml_file path, need to check to see if new camera has different coordinates for the crosswalk
# returns array of coordinates
# need to replace crosswalk coordinates
# use an xml to find it perma
def get_crosswalk_coordinates():
    coordinates = [[514, 796], [721, 783], [1095, 934], [763, 992]]
    return np.array(coordinates)

# the following function is used in testing if expanded crosswalk coordinates would be better,
# but helps us keep the highlighted portion of the crosswalk for the viewer to understand better
def get_highlightable_coordinates():
    coordinates = [[524, 802], [667, 790], [1023, 941], [758, 962]] # for highlighting the crosswalk
    return np.array(coordinates)

# parse the xml file
# gets object, bndbox (bounding box for the objects), and check if the object is equal to a person
# returns list all objects 
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


# multiple boxes per object, compresses into just one box for the object
# finds overlap between pictures, if there are no object boxes, skip the picture
def non_max_suppression_fast(boxes, overlapThresh):
    print("NON MAX SUPRESSION FAST")
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
    global dict_person_assigned_number_frames
    try:
        return max(dict_person_assigned_number_frames, key=dict_person_assigned_number_frames.get)   
    except:
        return 0  

#3
def update_current_frame_assignments(current_frame_persons, current_frame_sim_score,
                                     max_score, max_person_id, best_match_number):
    print("UPDATE CURRENT FRAME ASSIGNMENTS")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    print("max_Score=",max_score, "max_person_id= ", max_person_id, "previous_frame_match = ", best_match_number)
    print("First if", current_frame_sim_score)
    if max_person_id in current_frame_sim_score:
        del current_frame_sim_score[max_person_id] 

    print("Second", current_frame_sim_score)    
    if max_person_id == -1:
        print(current_frame_sim_score)
        for current_id, current_person in enumerate(current_frame_persons):
            print("current_frame_persons",current_person.assigned_number, current_person.person_id)
#             if current_person.person_id == current_person_id:
            if current_person.assigned_number == 0:                 #PROBLEM FOUND HERE
                print(current_person.assigned_number, "CASE 1")
                current_frame_persons[current_id].assigned_number = get_total_person_count(
                    current_frame_persons)+1    #ADD 1 TO TOTAL PERSON COUNT BUT DOESN'T UPDATE TOTAL
                print("Assigned number = ", current_frame_persons[current_id].assigned_number)
                #dict_person_assigned_number_frames[current_frame_persons[current_id].assigned_number] = []

    print("Third", current_frame_sim_score)
    for current_id, current_person in enumerate(current_frame_persons):  
        if current_person.person_id == max_person_id:
            if max_score > 0.6:
                print(current_frame_persons[current_id].assigned_number, "CASE 2")
                current_frame_persons[current_id].assigned_number = best_match_number
                print("Max score > 0.6, assigned number = ", best_match_number)
            else:
                print(current_frame_persons[current_id].assigned_number, "CASE 3")
                current_frame_persons[current_id].assigned_number = get_total_person_count(current_frame_persons)+1
                print("Max score <= 0.6, assigned number = ", current_frame_persons[current_id].assigned_number)

    print("Fourth", current_frame_sim_score)
    for person_id, scores in list(current_frame_sim_score.items()):
        for k, v in list(current_frame_sim_score[person_id].items()):
            if k == best_match_number:
                print("Person ID: ", person_id)
                print("Score: ", scores)
                print("Match Found", k)
                del current_frame_sim_score[person_id][k]     

    print("Fifth", current_frame_sim_score)
    return current_frame_persons,current_frame_sim_score


def is_all_current_frame_persons_assigned(current_frame_persons):
    print("IS ALL CURRENT FRAME PERSONS ASSIGNED")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    for current_id, current_person in enumerate(current_frame_persons):
        if current_person.assigned_number == 0:
            print(False)
            return False
    print(True)
    return True

#2
def find_best_match_score(frame_queue, current_frame_persons, current_frame_sim_score,total_person_count):
    print("FIND BEST MATCH SCORE")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    while(not is_all_current_frame_persons_assigned(current_frame_persons)):
        max_score, max_person_id, best_match_number = 0, -1, -1
        for person_id, scores in list(current_frame_sim_score.items()):
            sim_score = current_frame_sim_score[person_id]
            print("Pratool", person_id, sim_score)
            if len(sim_score) > 0 and max(sim_score.values()) > max_score: #HERE?
                max_score = max(sim_score.values()) #get max value in sim_score -> sim_score is all similarity scores b/w person Id and other people
                max_person_id = person_id
                best_match_number = max(sim_score, key=sim_score.get)
                print("Best match: " + str(best_match_number))
        current_frame_persons,current_frame_sim_score = update_current_frame_assignments(
            current_frame_persons, current_frame_sim_score, max_score, max_person_id, best_match_number)
    frame_queue, current_frame_persons = update_previous_frame(frame_queue, current_frame_persons)   
    #print("Current frame persons" + str(current_frame_persons)) 
    return current_frame_persons, frame_queue

#4, maybe this function could fix the same id in the same frame
def update_previous_frame(frame_queue, current_frame_persons):
    print("UPDATE PREVIOUS FRAME")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
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
    print("ASSIGN NUMBERS TO PERSON")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
    if not any(frame_queue): 
        print("No frame queue:")
        for current_id, current_person in enumerate(current_frame_persons):
            print("Current ID: " + str(current_id))
            total_person_count+=1
            current_frame_persons[current_id].assigned_number = total_person_count
        return current_frame_persons
    else:
        print("Frame queue:")
        current_frame_sim_score=dict()
        for current_id, current_person in enumerate(current_frame_persons):            
            sim_score = defaultdict(list)
            print("current person", current_person.person_id)
            for previous_frame in frame_queue:
                for previous_person in previous_frame.person_records:
                    similarity_score=cos(
                        current_person.feature,previous_person.feature).cpu().numpy()
                    sim_score[previous_person.assigned_number].append(similarity_score) #assigns a sim score to the prev person's assigned number
                    print("Previous Frame", previous_person.assigned_number )
                    print("Frame id: ", previous_frame.frame_id)
                    print("Sim score: " + str(similarity_score) + "\n")
            for assigned_number in sim_score:
                sim_score[assigned_number] = np.median(sim_score[assigned_number])
            current_frame_sim_score[current_person.person_id] = sim_score  
            print("Person Details", current_person.person_id, current_person.center_cords,sim_score)
        print("Call find best match score")
        return find_best_match_score(frame_queue, current_frame_persons, current_frame_sim_score, total_person_count)

#Adds the person position and the frame they're located in to the dictionaries
def update_person_position_and_frame(current_frame_persons,person_pos, current_frame_id ):
    print("UPDATE PERSON POSITION AND FRAME")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    global dict_person_assigned_number_frames
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
    print("Person Pos: " + str(person_pos))    
    return person_pos


def update_person_frame(current_frame_id,frame_queue,person_pos):
    print("UPDATE PERSON FRAME")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    global dict_person_assigned_number_frames
    for assigned_number in list(dict_person_assigned_number_frames.keys()):
        arr = dict_person_assigned_number_frames[assigned_number]
        if len(arr) == 1:
            if current_frame_id - arr[0] > 0:
                print(current_frame_id, arr,assigned_number )
                print("CASE 1")
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
                    
        elif len(arr) == 2:
            if arr[1]-arr[0] > 1:
                print("CASE 2")
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
    # print(dict_person_assigned_number_frames)
    # print("Queue Length", len(frame_queue))
    #print("Frame Queue: " + str(frame_queue) + ", Person Pos: " + str(person_pos))
    return frame_queue,person_pos

def middle_between_points(point1, point2):
    middle = [None] * 2
    middle[0] = (point1[0] + point2[0]) // 2 #x coordinate
    middle[1] = (point1[1] + point2[1]) // 2 #y coordinate
    return middle

#Checks the proximity between 2 points within a set threshold
def check_proximity(point1, point2):
    y_thresh = 500
    delta_y = point1[1] - point2[1]
    if delta_y <= y_thresh or delta_y >= -y_thresh:
        x_thresh = 300
        delta_x = point1[0] - point2[0]
        if delta_x <= x_thresh or delta_x >= -x_thresh:
            return True
    return False

#checks if a point is on the edge of the screen within 
#a bounds
def check_if_on_edge(last_point, point):
    if abs(2550 - point[0]) < 400:
        if last_point[0] < point[0]: return True
    elif abs(0-point[0]) < 400:
        if last_point[0] > 400: return True

    if abs(1920 - point[1]) < 400:
        if last_point[1] < point[1]: return True
    elif abs(0-point[1]) < 400:
        if last_point[1] > point[1]: return True

    return False

def check_in_image_box(point):
    image_poly = Polygon([(120, 0), (120, 1500), (1900, 1500), (1900,0)])
    if image_poly.contains(point):
        return True
    return False
        
# GLOBAL VARIABLES TO FIND LINES ON THE ROAD
# 0.0428455942 puts me at 29
north_road_slope = .0684754522
north_ycoord = 870
south_road_slope = 0.0933
south_ycoord = 1025
# sometimes returns true when it shouldnt
def did_person_cross_the_road(assigned_number, person_pos):
    print("DID PERSON CROSS THE ROAD")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    #crossing the road conditions
    north_side = False #condition_1
    south_side = False #condition_2
    #values for each side of the road, change these for new images

    #get crosswalk coords
    crosswalk_coords = get_crosswalk_coordinates()
    center_top = middle_between_points(crosswalk_coords[0], crosswalk_coords[1])
    center_bottom = middle_between_points(crosswalk_coords[2], crosswalk_coords[3])

    arr = []
    if assigned_number in person_pos:
        current_person_pos = person_pos[assigned_number]
        for cords in current_person_pos:
            print(cords)
            if (north_road_slope*cords[0])+cords[1]-north_ycoord < 0: # use middle of road
                north_side = True
            if (south_road_slope*cords[0])+cords[1]-south_ycoord > 0:
                south_side = True
            if (north_road_slope*cords[0])+cords[1]-north_ycoord > 0 and (south_road_slope*cords[0])+cords[1]-south_ycoord < 0: #use middle of sidewalk
                arr.append(cords)
    if len(arr) > 1:
        distance_covered = float(Point(arr[0]).distance(Point(arr[-1])))
        total_distance = float(Point(center_top).distance(Point(center_bottom)))
        pct = distance_covered/ total_distance
        print ("assigned_number = ", assigned_number, "distance_covered = ", distance_covered, "total_distance = ",
              total_distance, "pct = ", pct, "cords = ", arr[0], arr[-1])
        if (north_side and south_side) or (north_side and pct>0.8) or (south_side and pct>0.8):
            return True
    return False

def angle_between_crosswalk_and_trajectory(person_pos):
    print("ANGLE BETWEEN CROSSWALK AND TRAJECTORY")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    import math
    from sympy import Point, Line, pi
    first_point = 0
    second_point = 0
    flag = True

    #get crosswalk coords
    crosswalk_coords = get_crosswalk_coordinates()
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

# sometimes returns true when it shouldnt
def did_person_use_the_crosswalk(person_cords, crosswalk_cords):
    print("DID PERSON USE THE CROSSWALK")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    count=0
    # using the crosswalk coordinates
    # NOTE - FOR SHOW ONLY, NOT ACTUAL CROSSWALK COORDS BEING USED
    crosswalk_polygon = Polygon([(524,802),(667,790),(1023,941),(758,962)])
    #print("Pratool person cords",person_cords)
    for cords in person_cords:
        if crosswalk_polygon.contains(Point(cords)):
            count+=1
    if count>1:
        return True
    return False

def color_the_person_box(img_original, assigned_number, person_pos, person_cords, crosswalk_cords, 
                         val,dict_person_crossed_the_road, dict_person_use_the_crosswalk):
    print("COLOR THE PERSON BOX")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    if did_person_cross_the_road(assigned_number, person_pos):
        #angle = angle_between_crosswalk_and_trajectory(person_pos[assigned_number])
        if assigned_number not in dict_person_crossed_the_road:
            dict_person_crossed_the_road[assigned_number] = True
            # check this
        if did_person_use_the_crosswalk(person_cords, crosswalk_cords):# and any(x<25 or x>155 for x in angle):
            if assigned_number not in dict_person_use_the_crosswalk:
                dict_person_use_the_crosswalk[assigned_number] = True
                # check this
            cv2.rectangle(img_original,(val[1],val[2]),(val[3],val[4]),(0,255,0),5)#green 
        else:
            cv2.rectangle(img_original,(val[1],val[2]),(val[3],val[4]),(0,0,255),5)#red
    else:
        cv2.rectangle(img_original,(val[1],val[2]),(val[3],val[4]),(255,255,255),3)#white
        
    return img_original, dict_person_crossed_the_road, dict_person_use_the_crosswalk

def main():
    image_list=[]
    date_arr=[] 
    global dict_person_assigned_number_frames, dict_person_crossed_the_road, dict_person_use_the_crosswalk, dict_frame_time_stamp
    current_frame_persons=[]
    count = 0
    person_id=1
    total_person_count=0
    frame_id=0
    frame_queue = deque([],5) #original is 5
    person_pos = dict()
    frame_record = recordtype("frame_record", "frame_id person_records")
    person_record = recordtype("person_record", "person_id frame_id feature assigned_number center_cords bottom_cords")

    if len(sys.argv) < 2:
        print("\n \nFormat: python pedestrian_detection.py [date1, date2, ...]")
        print("Where dateN = yyyy/mm/dd ")
        return

    for arg in sys.argv:
        date_arr.append(arg)

    dict_person_crossed_the_road = dict()
    dict_person_use_the_crosswalk = dict()
    dict_person_assigned_number_frames = dict()
    dict_frame_time_stamp = dict()

    size = (0,0)

    global max_person_count
    max_person_count=0

    for day in date_arr:
        PATH_TO_IMAGES_DIR = pathlib.Path('/raid/AoT/sage/000048B02D15BC7D/bottom/'+ day + '/')
        TEST_RAW_IMAGE_PATHS = sorted(list(PATH_TO_IMAGES_DIR.rglob("*.jpg")))

        for im in TEST_RAW_IMAGE_PATHS:
            try:
                file_name = os.path.basename(im)
                var_date_time = file_name[:len(file_name)-4].split("T")
                var_date_str, var_time_str = var_date_time[0], var_date_time[1]
                # print("printing var date str: ", var_date_str, " -> end of var date str")
                var_time_str = var_time_str.replace('+0000','')
                var_time_object = datetime.strptime(var_time_str, "%H:%M:%S")
                var_date_object = datetime.strptime(var_date_str, "%Y-%m-%d")
                formatted = "{:02d}".format(var_date_object.month) + "-" + str(var_date_object.day) + "-" + str(var_date_object.year)
                file_name = file_name.replace('.jpg','')
                if 13 <= var_time_object.hour and var_time_object.hour <= 13: 
                    xml_file = "/raid/AoT/image_label_xmls/" + str(formatted) + "/new_xmls/"+file_name+".xml"
                    print(xml_file)
                    if not os.path.isdir('/raid/AoT/image_label_xmls/crosswalk_detections'): # adds crosswalk_detections directory
                        os.mkdir('/raid/AoT/image_label_xmls/crosswalk_detections')
                    if not os.path.isdir('/raid/AoT/image_label_xmls/crosswalk_detections/' + var_date_str): # adds day to directory
                        os.mkdir('/raid/AoT/image_label_xmls/crosswalk_detections/' + var_date_str)
                    if os.path.exists(xml_file):
                        frame_id+=1
                        frame_rec = frame_record(0,0)
                        frame_rec.frame_id = frame_id
                        print("Frame id", frame_id )
                        current_frame_persons=[]
                        
                        person_coordinates = parse_xml(xml_file) # get the coordinates for a person in the picture
                        person_coordinates = non_max_suppression_fast(np.array(person_coordinates),0.3)

                        if len(person_coordinates)>0:            # checking to see if a person is within the picture
                            print("Printing person coordinates: ", person_coordinates)
                            img_original = cv2.imread(str(im))   # img_original now holds the image
                            img_c = img_original.copy()          # a copy of the original
                            pts = get_highlightable_coordinates()# uses non padded crosswalk coordinates as a highlighter for visual aid
                            temp_arr=[]
                            for person in person_coordinates:
                                if person[0] < 1900 and abs((person[1]-person[3]) * (person[0]-person[2])) > 2200:
                                    if frame_id not in dict_frame_time_stamp:
                                        dict_frame_time_stamp[frame_id] = var_date_time
                                    print("Person: ", person , " - end person print")
                                    img = img_original[person[1]:person[3], person[0]:person[2]]
            #                         print((person[1]-person[3]) * (person[0]-person[2]))
            #                         print("Index = ", count, "Image Shape = ",img.shape)
                                    person_rec = person_record(0,-1,0,0,0,0)
                                    person_rec.person_id = person_id
                                    person_rec.frame_id = frame_rec.frame_id 
            #                         print(np.average([person[0],person[2]]))
                                    print("xml file",xml_file)
                                    person_rec.center_cords = [int(np.average([person[0],person[2]])), person[3]] # finds the center of the bounding box
                                    print("center coords: ", person_rec.center_cords)
                                    person_rec.feature = extractor(img)
                                    #print("Printing person_rec.feature: ")
                                    #print(person_rec.feature)
                                    #print("end person rec feature")
                        
            #                         print(person_id, person)
                                    
                                    current_frame_persons.append(person_rec)
                                    
            #                         cv2.rectangle(img_original,(person[0],person[1]),(person[2],person[3]),(0,255,0),3)
                                    temp_arr.append([person_id, person[0],person[1], person[2], person[3]])
                                    print("Temp arr: " + str(temp_arr))
                                    
                                    person_id+=1
                                    # if person_id> 100000:
                                    #     person_id=1
            #                 frame_queue, person_pos=update_person_frame(frame_id,frame_queue, person_pos)        
                            assign_numbers_to_person(frame_queue, current_frame_persons, total_person_count)
                            
                            person_pos = update_person_position_and_frame(current_frame_persons, person_pos, frame_rec.frame_id)
            #                 print(person_pos)
                            frame_queue, person_pos = update_person_frame(frame_id,frame_queue, person_pos)
                            total_person_count = get_total_person_count(current_frame_persons)
                            
                            for curr_person in current_frame_persons:
                                print("Person id: " + str(curr_person.person_id))
                                person_cross_the_road = did_person_cross_the_road(curr_person.assigned_number,person_pos)
                                print("Current person", person_cross_the_road)
                                if person_cross_the_road:
                                    print(curr_person.assigned_number, 
                                        did_person_use_the_crosswalk(person_pos[curr_person.assigned_number], pts))
                            
            #                 if total_person_count == 0:
            #                     total_person_count = max_person_count
            #                 else:
            #                     max_person_count = total_person_count
                            frame_rec.person_records = current_frame_persons
                            frame_queue.append(frame_rec)
                            print("Total person count", total_person_count)
                            for val in temp_arr:
                                for p_id, p_val in enumerate(current_frame_persons):
                                    if current_frame_persons[p_id].person_id == val[0]:
                                        img_original, dict_person_crossed_the_road, dict_person_use_the_crosswalk = color_the_person_box(img_original, 
                                                             current_frame_persons[p_id].assigned_number, 
                                                             person_pos, 
                                                             person_pos[current_frame_persons[p_id].assigned_number], 
                                                             pts,
                                                             val,
                                                             dict_person_crossed_the_road,
                                                             dict_person_use_the_crosswalk)
                                        cv2.putText(
                                            img_original, str(
                                                current_frame_persons[p_id].assigned_number), (
                                                val[1],val[2]-30), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,255), 5)

                                               
                            # fills the crosswalk yellow
                            cv2.fillPoly(img_original, pts = [pts], color=(0,255,0))
                            # add sloped lines for road
                            # NOTE - NOT ACTUAL LINES USED - MOSTLY FOR SHOW
                            # add vertical line down middle
                            #cv2.line(img_original,(1286,0),(1286,1900),(0,255,255),5)
                            # give transparency to all the stuff shown on the image
                            cv2.line(img_original,(0,860),(2550,700),(0,0,255),8)
                            cv2.line(img_original,(0,1025),(2550,800),(0,0,255),8)

                            img_new = cv2.addWeighted(img_c, 0.3, img_original, 1 - 0.3, 0)
                            # Writing onto the image original person count, person used road or crosswalk stated
                            cv2.putText(img_new, "Person count = "+ str(total_person_count), (
                                                50, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,255,239), 6)
                            cv2.putText(img_new, "Person crossed road = "+ str(len(dict_person_crossed_the_road)), (
                                                50, 260), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,255,239), 6)  
                            cv2.putText(img_new, "Person used crosswalk = "+ str(len(dict_person_use_the_crosswalk)), (
                                                50, 400), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,255,239), 6)                      

                            # used for video writer
                            height, width, layers = img_new.shape
                            size = (width,height)
                            image_list.append(img_new)
                            # Saves file with writing to the path
                            cv2.imwrite('/raid/AoT/image_label_xmls/crosswalk_detections/' + var_date_str + "/" + file_name + ".jpg", img_new)
                            #cv2.imwrite("/raid/AoT/image_label_xmls/08-31-2021/written/newest/" + file_name + '.jpg', img_new)
                            # plt.imshow(cv2.cvtColor(img_new, cv2.COLOR_BGR2RGB))
                            # plt.show()   
                            print("\n") 
                        else:
                            frame_queue, person_pos =update_person_frame(frame_id,frame_queue,person_pos)
            except Exception as e:
                print(str(e))
                continue
    
    #create video of day/hour
    out = cv2.VideoWriter('/raid/AoT/image_label_xmls/crosswalk_detections/' + var_date_str + '/crosswalk_detection.mp4',cv2.VideoWriter_fourcc(*'mp4v'),15,size)
    for i in range(len(image_list)):
        out.write(image_list[i])
    out.release()

    # dont worry about, used for extraction later on
    with open('person_cords_2021-10-04.pickle', 'wb') as handle1:
        pickle.dump(person_pos, handle1, protocol=pickle.HIGHEST_PROTOCOL)

    with open('person_frames_2021-10-04.pickle', 'wb') as handle2:
        pickle.dump(dict_person_assigned_number_frames, handle2, protocol=pickle.HIGHEST_PROTOCOL)

    with open('frame_timestamps_2021-10-04.pickle', 'wb') as handle3:
        pickle.dump(dict_frame_time_stamp, handle3, protocol=pickle.HIGHEST_PROTOCOL)
    #save person coordinates
    import csv
    a_file = open("/raid/AoT/image_label_xmls/crosswalk_detections/" + var_date_str + "/person_cords.csv", "w")
    writer = csv.writer(a_file)
    for key, value in person_pos.items():
        writer.writerow([key, value])
    a_file.close()

    #print still image of all the crosswalk trajectories
    print("Tracing trajectories...")
    from plot_lines import draw_lines
    draw_lines(var_date_str)

    #save assigned number of frames per person
    b_file = open("/raid/AoT/image_label_xmls/crosswalk_detections/" + var_date_str + "/person_frames.csv", "w")
    writer = csv.writer(b_file)
    for key, value in dict_person_assigned_number_frames.items():
        writer.writerow([key, value])
    b_file.close()

    #save frame timestamps
    c_file = open("/raid/AoT/image_label_xmls/crosswalk_detections/" + var_date_str + "/frame_timestamps.csv", "w")
    writer = csv.writer(c_file)
    for key, value in dict_frame_time_stamp.items():
        writer.writerow([key, value])
    c_file.close()


if __name__ == '__main__':
    main()
