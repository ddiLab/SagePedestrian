from datetime import date
from datetime import timedelta
import sys
import json
from SageBokeh import bokeh_heat_map
from SageBokeh import bokeh_double_line_graph
from SageBokeh import bokeh_double_scatter_plot
from SageBokeh import bokeh_direction_scatter_plot
import time

sys.path.insert(0, '/home/wesley/')
import server_info

def last24():
    #get yesterday's date
    today = date.today()
    non_string_yesterday = today - timedelta(days = 1)
    yesterday = str(non_string_yesterday)
    yesterday = yesterday.replace("/","-")
    #query to get all coordinates from yesterday
    query = "SELECT PERMAID, XCOORD, YCOORD FROM Coordinate WHERE DATE LIKE '" + yesterday + "%' order by PERMAID;"

    #connect to db
    connection = server_info.connect_to_database()
    db_cursor = connection.cursor()
    db_cursor.execute(query)

    record = db_cursor.fetchall() # [0] = perma id, [1] = xcoord, [2] = ycoord
    #print(record)
    total_coords = []

    path_dict = {}

    #if len(record) < 1 or record is None:  #if record is empty
    #    print("None")
    #else:
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

    print(json.dumps(path_dict)) #print the path dictionary so php can retrieve it
    #create charts
    bokeh_heat_map(db_cursor)
    bokeh_double_line_graph(db_cursor)
    bokeh_double_scatter_plot(db_cursor)
    bokeh_direction_scatter_plot(db_cursor)

    db_cursor.close()
    connection.close()

if __name__ == '__main__':
    last24()
