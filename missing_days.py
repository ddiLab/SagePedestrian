'''
THIS SCRIPT IS DESIGNED TO RUN ONCE A WEEK AT THE END OF THE WEEK (SUNDAYS)

IT CHECKS FOR MISSING DAYS FOR THE SAGE CROSSWALK DETECTION PROJECT BY LOOKING AT THE 
IMAGE_LABEL_XMLS DIRECTORY TO SEE IF XMLS EXIST FOR THE DAY, IF THEY DO IT FURTHER CHECKS
TO SEE IF THERE ARE IMAGES IN THE IMAGE_LABEL_XMLS/CROSSWALK_DETECTIONS DIRECTORY
'''

############################################################################
#                                                                          #
#                                                                          #
#   First step: find all of the days of the week based on the current day  #
#                                                                          #
#                                                                          #
############################################################################
import datetime


today = datetime.date.today()    # get the current date: YYYY-MM-DD
weekday_num = today.isoweekday() # get the week day based on current day (1-7 (Sun = 7))
print("Today: ", today, " | Day: ", weekday_num, "/7")

'''
THANKS TO THIS STACK OVERFLOW LINK https://stackoverflow.com/questions/56163008/how-to-get-all-dates-of-week-based-on-week-number-in-python
FOR PROVIDING A SIMPLE EASY WAY TO GET ALL THE DAYS OF THE WEEK
'''

start_of_week = today - datetime.timedelta(days=weekday_num) # get the first day of the week

days_to_check = []               # array that we will be checking for xml/image existences

# get all of the days of the week for the current week 
for i in range(7):       
    days_to_check.append(start_of_week + datetime.timedelta(days=i))

days_to_check = [str(d) for d in days_to_check] # convert the days from dates to strings

print("Dates in week: ", days_to_check)

# FORMAT OF DAYS TO CHECK AT THIS POINT = ['YYYY-MM-DD',...]

############################################################################
#                                                                          #
#   Second step: Filter the string array of dates by checking to see       #
#                which ones have no images found in                        #
#                /raid/AoT/image_label_xmls/crosswalk_detections/          #
#                                                                          #
############################################################################

filtered_dates_to_check = [] # Keeps track of the dates that have NO data from pedestrian detection in crosswalk_detections/

# crosswalk detection directory name format: YYYY-MM-DD

import os

for day in days_to_check:
    path_to_pd_imgs = "/raid/AoT/image_label_xmls/crosswalk_detections/" + day # get path to particular day
    dir_exists = os.path.isdir(path_to_pd_imgs)                                # check to see if the directory for that day exists
    #print("Day: " + day, " |", " DIR: ", dir_exists)
    if dir_exists == False:
        filtered_dates_to_check.append(day) # append the days that do not have images to the array we need to re-run

#print(filtered_dates_to_check)

############################################################################
#                                                                          #
#   Third step: Now that we have the days with no images, we need to see   #
#               if the xmls exist for that day in /image_label_xmls        #
#                                                                          #
############################################################################

xmls_but_no_imgs = [] # array that stores list of days with no images but xmls do exist
no_xmls = []          # array that stores list of days with no xmls (thus no images)

# the file format for image_label_xmls is different than crosswalk_detections
# need to get MM-DD-YYYY format instead

temp_array = filtered_dates_to_check
filtered_formatted_dates_to_check = [] # python is dumb and wont append a cleared array so i made this for now

for day in temp_array:
    year = day[0:4]
    month = day[5:7]
    new_day = day[8:10]
    new_date_format = month + "-" + new_day + "-" + year
    filtered_formatted_dates_to_check.append(new_date_format)

for day in filtered_formatted_dates_to_check:
    path_to_xmls = "/raid/AoT/image_label_xmls/" + day
    dir_exists = os.path.isdir(path_to_xmls)  # check to see if the directory exists
    #print("Day: " + day, " | ", "Dir Exists: ", dir_exists)
    if dir_exists == True:                    # if it does, check to see if there is 30k-36k xmls
        file_count = 0                        # counter to see how many files are in the directory (dont rerun day if > 30k)
        for path in os.listdir(path_to_xmls): 
            file_count = file_count + 1       # get file count
        #print("     File Count: ", file_count)
        if file_count > 30000:
            xmls_but_no_imgs.append(day)
        else:
            no_xmls.append(day)
    else:
        no_xmls.append(day)

print("NO XMLS: ", no_xmls)
#print("XMLS BUT NO IMGS: ", xmls_but_no_imgs)

############################################################################
#                                                                          #
#                               Fourth step:                               #
#                                                                          #
#   Now we have two lists that determine if:                               #
#       1)xmls exist but images dont  - xmls_but_no_imgs                   #
#       2)no xmls exist (thus no images)  - no_xmls                        #
#                                                                          #
#   The goal for this step is to get these combined into one array         #
#   that will only be xmls exist but images dont - xmls_but_no_imgs        #
#                                                                          #
#   To achieve that we will do object detection for those days             #
#                                                                          #
############################################################################

# NOTE: IMPORTANT: 
# !!! THIS SCRIPT RUNS ON SUNDAY BUT RUNS LAST WEEKS SUNDAY !!!
# FOR EXAMPLE: TODAY IS SUNDAY 9/11/2022, BUT WHEN RUN, THE SUNDAY FOR THAT WEEK IS 9/4/2022

import script_object_detection

for day in no_xmls:
    print("Running object detection for: " + day)
    script_object_detection.main(day)  # xmls created for missing day
    xmls_but_no_imgs.append(day)       # add this to the xml but no images (ready for pedestrian detection)
    print("Finished object detection for: " + day)


import pedestrian_detection

for day in xmls_but_no_imgs:
    # need to get correct date formatting for pedestrian detection call (have MM-DD-YYYY, need YYYY/MM/DD)
    pedestrian_day = day[3:5]
    pedestrian_month = day[0:2]
    pedestrian_year = day[6:10]
    pedestrian_date = pedestrian_year + "/" + pedestrian_month + "/" + pedestrian_day

    # Run pedestrian detection with the xmls_but_no_imgs list
    pedestrian_detection.main(interval=-1, date=pedestrian_date, plot=True, initial=True)
