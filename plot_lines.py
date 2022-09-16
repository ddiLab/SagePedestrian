import sys
import cv2
import numpy as np

sys.path.insert(0, '/home/wesley/')
import server_info

#Some improvements: Do the hourly and master plots at the same time
#                   Only pull information from the database once
def draw_lines():
    master_image_path = "/var/www/html/images/image2.jpg"
    output_image_path = "/home/wesley/image_output/"

    image = cv2.imread(master_image_path)
    image_copy = image.copy()
    master_copy = image.copy()

    #connect to db
    connection = server_info.connect_to_database()
    db_cursor = connection.cursor()
    #get most recent date
    most_recent_day_query = "select max(DATE_FORMAT(DATE, '%Y-%m-%d')) from Contains"
    db_cursor.execute(most_recent_day_query)
    record = db_cursor.fetchall()
    
    if record is None or len(record) < 1: return

    new_date = record[0][0]
    time_start = new_date + " 13:00:00"
    time_stop = new_date + " 22:59:59"
    #query to get all coordinates from yesterday
    query = "SELECT PERMAID, XCOORD, YCOORD FROM Coordinate WHERE DATE between '" + time_start + "' and '" + time_stop + "' order by PERMAID, DATE;"

    db_cursor.execute(query)

    record = db_cursor.fetchall() # [0] = perma id, [1] = xcoord, [2] = ycoord
    total_coords = []
    path_dict = {}

    if len(record) >= 1 and record is not None:
        #store all records in a list
        perma_id = record[0][0]
        for row in record:
            if(row[0] != perma_id):
                perma_id = row[0]
                total_coords.clear()
                coordinate = (row[1],row[2])
                total_coords.append(coordinate)
            else:
                coordinate = (row[1],row[2]) # tuple of the rows coordinates
                total_coords.append(coordinate)
                if perma_id not in path_dict:
                    path_dict[perma_id] = []
                path_dict[perma_id].append(coordinate)
    

    #for i in range(0, 20):
    alpha = 0.35
    overlay = image.copy()
    master_copy = image.copy()
    for person,points in path_dict.items():
        color = None
        if points[0][1] > 1200: color = (255, 0, 0)
        else: color = (0, 0, 255)
        overlay = cv2.polylines(overlay, np.int32([points]), False, color, 2)
        master_copy = cv2.addWeighted(overlay, alpha, image, 1-alpha, 0)
    cv2.putText(master_copy, "Transparency: {:.2f}".format(alpha), (150, 1750), cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 255), 6)
    cv2.imwrite(output_image_path + 'alpha{:.2f}'.format(alpha) + '.jpg', master_copy)

    db_cursor.close()
    connection.close()
    return

# for using the script without pedestrian_detection.py, for testing
if __name__ == '__main__':
    draw_lines()
