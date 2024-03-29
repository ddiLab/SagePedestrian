# Sage Pedestrian
Pedestrian tracking with data from NSF Sage Project
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**env.yml:** Conda environment to run scripts     
**plot_object_detection.py:** Run the images through the object detection model and spits out an xml file containing the results   
**pedestrian_detection.py:** Parse xml files and track people in the photo using re-id     
**plot_lines.py:** Using database information to trace trajectories and write them to an image (hourly and daily)    
**SagePedestrian.sql:** Sql script that creates the tables for the pedestrian detection database     
**requirements.txt:** Environment creation for non Conda environments    

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Students:** Justin Derus, Wesley Kwiecinski                   
**Mentors:** Pratool Bharti, Michael Papka            
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Useful Sources:**  
Tutorial to create conda env: https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment

Open CV Image Writing: https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html (Python is below c++) 

Open CV Line Drawing Documentation: https://docs.opencv.org/4.x/dc/da5/tutorial_py_drawing_functions.html 

Object Detection Tutorial: https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_saved_model.html  

Deep Re-id: https://github.com/KaiyangZhou/deep-person-reid  

Cronjob Tutorial: https://www.hostinger.com/tutorials/cron-job 

Machine Learning Tutorial: https://www.youtube.com/playlist?list=PLQY2H8rRoyvz_anznBg6y3VhuSMcpN9oe 

Node.js and NVM: https://ostechnix.com/install-node-js-linux/            


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**STEPS TO GETTING THE CODE UP AND RUNNING (on hartley):**

0) Clone this github repo
1) Create and activate a new [conda environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment) using the provided env.yml file (yml file may not include all packages, just run code and install packages as necessary)
2) Clone [the deep-person-reid repo](https://github.com/KaiyangZhou/deep-person-reid) into this cloned repository. You shouldn't need to install it, make sure it's in the directory where you are running the script.
4) Make sure that the .xml files for the day you run exist in this directory /raid/AoT/image_label_xmls/ 
5) To run the pedestrian_detection script STANDALONE, follow this format: "python pedestrian_detection.py [hour_min] [hour_max] [date1, date2, ...]"
  - Where hours are optional, dateN = yyyy/mm/dd
6) Otherwise running plot_object detection will call pedestrian_detection and plot lines.
7) If not running pedestrian detection alone, use python plot_object_detection.py, which will use current date.
8) The output of the pedestrian_detection.py script will be found in /raid/AoT/image_label_xmls/crosswalk_detections/(ran_date)

**TROUBLESHOOTING)**
 - If the code refuses to use the gpu, try adding this to your .bashrc script in your home directory
  export CUDA_VISIBLE_DEVICES=0
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/[user]/.conda/envs/tf_gpu/lib
  export PYTHONPATH=$PYTHONPATH:/home/[user]/work/models
  
 - "ModuleNotFoundError: No module named 'torchreid'" -> Double check the deep-reid path at the top of pedestrian_detection.py if you get this error, make sure it points to the deep-reid directory
    - For any "ModuleNotFoundError", "pip install [module_name]" will usually do the trick.
    - In the case of cv2, try: pip install opencv-python

 - If you are running a specified day on the plot_object_detection.py script and want it to run in the background, follow the steps commented at the top of that file
 
 - Plot Lines can be run standalone but you must change the date at the bottom of the script in __main__
 
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Database
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Database on snick.cs.niu.edu using mariadb under database pedestrian**
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Helpful MySQL commands:**

**Select all the people in a specific day with their coordinates** - select PERMAID,XCOORD,YCOORD from Coordinate where DATE like 'yyyy-mm-dd%';
 - to get specific times use YYYY-MM-DD HH:MM:SS
 
**Find ID's of the people who have crossed the road** - select PERMAID, USEROAD from Person where USEROAD = 1;
- replace USEROAD with USECROSSWALK for crosswalk

**Find out what days are in the database** - select DATE from Frame where DATE like 'yyyy-mm-dd%';

**Find the total number of people who used the crosswalk** - select count(PERMAID) from Person where USECROSSWALK = 1;

**Find the number of people who used the crosswalk in a certain day** - select count(a.PERMAID) from 
( select PERMAID from Person where USECROSSWALK = 1 INTERSECT select PERMAID from Contains where DATE LIKE '2022-05-09%' ) as a;

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Table Names** : Contains, Coorindate, Frame, Person

**Person**
```
+--------------+-------------+------+-----+---------+-------+
| Field        | Type        | Null | Key | Default | Extra |
+--------------+-------------+------+-----+---------+-------+
| PERMAID      | int(11)     | NO   | PRI | NULL    |       |
| DAYID        | int(11)     | NO   |     | NULL    |       |
| USECROSSWALK | smallint(6) | YES  |     | 0       |       |
| USEROAD      | smallint(6) | YES  |     | 0       |       |
| NS           | smallint(6) | YES  |     | NULL    |       |
| EW           | smallint(6) | YES  |     | NULL    |       |
+--------------+-------------+------+-----+---------+-------+
```
**Coordinate** 
```
+---------+----------+------+-----+---------+----------------+
| Field   | Type     | Null | Key | Default | Extra          |
+---------+----------+------+-----+---------+----------------+
| TOTAL   | int(11)  | NO   | PRI | NULL    | auto_increment |
| PERMAID | int(11)  | NO   | MUL | NULL    |                |
| DATE    | datetime | NO   | MUL | NULL    |                |
| XCOORD  | int(11)  | YES  |     | 0       |                |
| YCOORD  | int(11)  | YES  |     | 0       |                |
+---------+----------+------+-----+---------+----------------+
```
**Frame** 
```
+---------+-----------+------+-----+---------+-------+
| Field   | Type      | Null | Key | Default | Extra |
+---------+-----------+------+-----+---------+-------+
| DATE    | datetime  | NO   | PRI | NULL    |       |
| PATH    | char(128) | NO   |     | NULL    |       |
| FRAMEID | int(11)   | NO   |     | NULL    |       |
+---------+-----------+------+-----+---------+-------+
```
**Contains**
```
+---------+----------+------+-----+---------+-------+
| Field   | Type     | Null | Key | Default | Extra |
+---------+----------+------+-----+---------+-------+
| PERMAID | int(11)  | NO   | PRI | NULL    |       |
| DATE    | datetime | NO   | PRI | NULL    |       |
+---------+----------+------+-----+---------+-------+
```
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
![alt text](https://github.com/ddiLab/SagePedestrian/blob/main/line_result_M.jpg?raw=true)

*This material is based upon work supported by the National Science Foundation under Grant No. OAC 1935984.*
