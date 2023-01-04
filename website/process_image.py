import numpy as np
import json
import sys
sys.path.insert(0, '/home/justind/')
import server_info

def pi_chart_per_hour(db_cursor, date):
    from matplotlib import pyplot as pie
    #crosswalk uses per hour for sepcific 'date'
    query2 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%H') as hour from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains where DATE like '" + date + "%') group by hour;"
    #total number of crosswalk uses for 1 day
    db_cursor.execute(query2)
    results = db_cursor.fetchall()
    pie_labels = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    #format results
    hourly_xwalk_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for row in results:
        hourly_xwalk_data[int(row[1]) - pie_labels[0]] = row[0]

    data = np.array(hourly_xwalk_data, dtype=int)

    if all(num == 0 for num in data): return

    pie_labels = ["8am", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm"]

    for i in range(len(pie_labels)):
        if data[i] == 0:
            pie_labels[i] = ""
    
    fig,ax = pie.subplots()
    #print(hourly_xwalk_data)
    ax.pie(data, labels = pie_labels)
    title='Crosswalk usages per hour for ' + str(date)
    ax.set(aspect="equal", title=title)
    fig.savefig('./images/xwalk_pie_per_hr.png')

    pie.close(fig)

    return

def uses_per_hour(db_cursor, date):
    from matplotlib import pyplot as plt
    query2 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%H') as hour from Contains where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select distinct PERMAID from Contains where DATE like \'" + date + "%\') group by hour;"
    db_cursor.execute(query2)
    road_results = db_cursor.fetchall()
    query3 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%H') as hour from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains where DATE like \'" + date + "%\') group by hour;"
    db_cursor.execute(query3)
    cwalk_results = db_cursor.fetchall()
    #format results
    hours = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22] #use internal hours
    hourly_cwalk_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    hourly_road_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for res in cwalk_results:
        hourly_cwalk_data[int(res[1]) - hours[0]] = res[0]
    for res in road_results:
        hourly_road_data[int(res[1]) - hours[0]] = res[0]

    hours = ['8am', '9am', '10am', '11am', '12pm', '1pm', '2pm', '3pm', '4pm', '5pm']

    x = np.arange(len(hours)) # label locations
    width = 0.35
    fig, ax = plt.subplots()
    rects1 = ax.bar( x- width/2, hourly_cwalk_data, width, label="Crosswalk")
    rects2 = ax.bar(x + width/2, hourly_road_data, width, label="Road")
    ax.set_ylabel('Uses')
    ax.set_xlabel('Hours')
    ax.set_title('Number of Crosswalk and Road Uses Per Hour ' + str(date))
    ax.set_xticks(x, hours)
    ax.legend()
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    fig.tight_layout()
    fig.savefig('./images/uses_per_hour.png')
    
    plt.close(fig)

    return

def main(query, date):
    connection = server_info.connect_to_database()
    db_cursor = connection.cursor()
    db_cursor.execute(query)

    record = db_cursor.fetchall() # [0] = perma id, [1] = xcoord, [2] = ycoord
    #print(record)
    total_coords = []
    no_data = False

    path_dict = {}
    
    if len(record) < 1 or record is None:  #if record is empty
        print("No data available")
        no_data = True
    else:
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
                
    #we only want to do certain things if we actually have data to retrieve
    if not no_data:
        pi_chart_per_hour(db_cursor, date)
        uses_per_hour(db_cursor, date)
        #heatmap_per_hour(db_cursor)
        #create_line_chart(db_cursor)
        print(json.dumps(path_dict)) #print the path dictionary so php can retrieve it

    db_cursor.close()
    total_coords.clear()
    connection.close()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
