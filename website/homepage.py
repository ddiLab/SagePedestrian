import sys
import json
from SageBokeh import bokeh_heat_map
from SageBokeh import bokeh_double_line_graph
from SageBokeh import bokeh_double_scatter_plot
from SageBokeh import bokeh_direction_scatter_plot

sys.path.insert(0, '/home/wesley/')
import server_info

def most_recent_day():
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

    print(new_date)
    print(json.dumps(path_dict)) #print the path dictionary so php can retrieve it
    #create charts
    bokeh_heat_map(db_cursor)
    bokeh_double_line_graph(db_cursor)
    bokeh_double_scatter_plot(db_cursor)
    bokeh_direction_scatter_plot(db_cursor)

    db_cursor.close()
    connection.close()

if __name__ == '__main__':
    most_recent_day()
