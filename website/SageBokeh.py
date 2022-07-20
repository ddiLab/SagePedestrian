from bokeh.plotting import figure, show
from datetime import datetime, timedelta
from bokeh.models import LinearColorMapper, PrintfTickFormatter, BasicTicker, ColorBar, Range1d
from datetime import timedelta
from math import pi
import numpy as np
import pandas as pd
import json
from bokeh.embed import json_item
import sys
from bokeh.models import ColumnDataSource
sys.path.insert(0, '/home/wesley/')
import server_info
from bokeh.transform import dodge

#import plotly.express as px
#import pandas as pd

#THE SINGLE BAR GRAPH IS WORKING AS INTENDED
def bokeh_single_bar_graph(db_cursor): 
    crosswalk_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains) group by day order by day;"
    #road_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select distinct PERMAID from Contains) group by day order by day;"

    days = []
    xwalk_counts = []
    road_counts = []
    

    db_cursor.execute(crosswalk_query)
    crosswalk_raw = db_cursor.fetchall()

    last_date = None
    
    for res in  crosswalk_raw:
        current_date = datetime.strptime(res[1], '%Y-%m-%d %a')
        while last_date != None and (current_date - last_date).days > 1:
            last_date = last_date + timedelta(days=1)
            xwalk_counts.append(0)
            days.append(last_date.strftime('%Y-%m-%d %a'))
        xwalk_counts.append(int(res[0]))
        days.append(res[1])
        last_date = current_date
    

    fig = figure(x_range = days, plot_width = 600, plot_height = 600)
    fig.vbar(x = days, top = xwalk_counts, width = 0.5) # width = width of the bars in the bar graph
    fig.xaxis.major_label_orientation = pi/4 # puts dates in a / angle 
    fig.yaxis.axis_label = "Uses"
    fig.xaxis.axis_label = "Dates"
    fig.title.text = "Crosswalk Usages Per Day"
    fig.title.align = "center" # also does left and right
    #fig.title.text_color = "orange"
    fig.title.text_font_size = "25px"
    
    #item_text = json.dumps(json_item(fig, "barGraph"))
    #item = JSON.parse(item_text);
    #Bokeh.embed.embed_item(item);

    # show the results in SageBokeh.html
    show(fig)
    return

def bokeh_double_line_graph(db_cursor):
    crosswalk_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains) group by day order by day;"
    road_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select distinct PERMAID from Contains) group by day order by day;"

    days = []
    xwalk_counts = []
    road_counts = []

    db_cursor.execute(crosswalk_query)
    crosswalk_raw = db_cursor.fetchall()

    last_date = None
    
    for res in crosswalk_raw:
        current_date = datetime.strptime(res[1], '%Y-%m-%d %a')
        while last_date != None and (current_date - last_date).days > 1:
            last_date = last_date + timedelta(days=1)
            xwalk_counts.append(0)
            days.append(last_date.strftime('%Y-%m-%d %a'))
        xwalk_counts.append(int(res[0]))
        days.append(res[1])
        last_date = current_date
    
    db_cursor.execute(road_query)
    road_raw = db_cursor.fetchall()

    last_date = None
    
    for res in  road_raw:
        current_date = datetime.strptime(res[1], '%Y-%m-%d %a')
        while last_date != None and (current_date - last_date).days > 1:
            last_date = last_date + timedelta(days=1)
            road_counts.append(0) 
        road_counts.append(int(res[0]))
        last_date = current_date


    TOOLS = "pan,box_zoom,reset,wheel_zoom"
    fig = figure(x_range = days, y_range=Range1d(0, np.max(road_counts), bounds="auto"), plot_width = 1024, plot_height = 600, tools=TOOLS, toolbar_location="below")
    fig.line(days, xwalk_counts, line_width=2, color="red", legend_label="Crosswalk")
    fig.line(days, road_counts, line_width=2, color="blue", legend_label="Road")
    fig.xaxis.major_label_orientation = pi/4 # puts dates in a / angle 
    fig.yaxis.axis_label = "Uses"
    fig.xaxis.axis_label = "Day"
    fig.title.text = "Crosswalk Usages Per Day"
    fig.title.align = "center" # also does left and right
    #fig.title.text_color = "orange"
    fig.title.text_font_size = "25px"
    
    #item_text = json.dumps(json_item(fig, "barGraph"))
    #item = JSON.parse(item_text);
    #Bokeh.embed.embed_item(item);
    print(json.dumps(json_item(fig, "doublelinegraph")))

    return

def bokeh_double_scatter_plot(db_cursor):
    crosswalk_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains) group by day order by day;"
    road_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select distinct PERMAID from Contains) group by day order by day;"

    days = []
    xwalk_counts = []
    road_counts = []
    

    db_cursor.execute(crosswalk_query)
    crosswalk_raw = db_cursor.fetchall()

    last_date = None
    
    for res in crosswalk_raw:
        current_date = datetime.strptime(res[1], '%Y-%m-%d %a')
        while last_date != None and (current_date - last_date).days > 1:
            last_date = last_date + timedelta(days=1)
            xwalk_counts.append(0)
            days.append(last_date.strftime('%Y-%m-%d %a'))
        xwalk_counts.append(int(res[0]))
        days.append(res[1])
        last_date = current_date
    

    db_cursor.execute(road_query)
    road_raw = db_cursor.fetchall()

    last_date = None
    
    for res in road_raw:
        current_date = datetime.strptime(res[1], '%Y-%m-%d %a')
        while last_date != None and (current_date - last_date).days > 1:
            last_date = last_date + timedelta(days=1)
            road_counts.append(0) 
        road_counts.append(int(res[0]))
        last_date = current_date

    fig = figure(x_range = days, plot_width = 600, plot_height = 600)
    fig.scatter(days, xwalk_counts, color="red", legend_label="Crosswalk")
    fig.scatter(days, road_counts, color="blue", legend_label="Road")
    fig.xaxis.major_label_orientation = pi/4 # puts dates in a / angle 
    fig.yaxis.axis_label = "Number of Crosswalk Uses"
    fig.xaxis.axis_label = "Day"
    fig.title.text = "Crosswalk Usages Per Day"
    fig.title.align = "center" # also does left and right
    #fig.title.text_color = "orange"
    fig.title.text_font_size = "25px"
    
    #item_text = json.dumps(json_item(fig, "barGraph"))
    #item = JSON.parse(item_text);
    #Bokeh.embed.embed_item(item);

    return

#THE DOUBLE BAR GRAPH IS SORT OF WORKING BUT DOES NOT COVER ALL THE ITERATIONS
def bokeh_double_bar_graph(db_cursor):
    crosswalk_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains) group by day order by day;"
    road_query = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day from Contains where PERMAID in (select PERMAID from Person where USEROAD=1 intersect select distinct PERMAID from Contains) group by day order by day;"

    days = []
    xwalk_counts = []
    road_counts = []
    
    

    db_cursor.execute(crosswalk_query)
    crosswalk_raw = db_cursor.fetchall()

    db_cursor.execute(road_query)
    road_raw = db_cursor.fetchall()

    last_date = None
    
    for res in  crosswalk_raw:
        current_date = datetime.strptime(res[1], '%Y-%m-%d %a')
        while last_date != None and (current_date - last_date).days > 1:
            last_date = last_date + timedelta(days=1)
            xwalk_counts.append(0)
            days.append(last_date.strftime('%Y-%m-%d %a'))
        xwalk_counts.append(int(res[0]))
        days.append(res[1])
        last_date = current_date

    last_date = None
    
    for res in  road_raw:
        current_date = datetime.strptime(res[1], '%Y-%m-%d %a')
        while last_date != None and (current_date - last_date).days > 1:
            last_date = last_date + timedelta(days=1)
            road_counts.append(0)
        road_counts.append(int(res[0]))
        last_date = current_date

    myDict = {'days': (0,0)}

    insert_into_dict_count = 0
    for day in days:
        myDict[day] = xwalk_counts[insert_into_dict_count],road_counts[insert_into_dict_count]
        insert_into_dict_count = insert_into_dict_count + 1


    source = ColumnDataSource(data=myDict)
    fig = figure(x_range = days, plot_width = 600, plot_height = 600)


    glyph_count = 0
    for key in myDict:
        print(key)
        if glyph_count == 0:# skip the first iteration that holds the column formatting
            glyph_count = glyph_count + 1
            continue
        #TODO the following code does not create multiple glyphs, it instead loops through the dictionary
        # and takes the top values from each statistic
        else:#means we have moved past the days key and need to glyph the actual data
            fig.vbar(x = dodge('days', -0.25, range = fig.x_range), top = myDict[key][0], # top sets the highest and lowest from all of the data sets, do not need to set after this
                width = 0.2,source = source, color = "red")
            fig.vbar(x = dodge('days', 0.00, range = fig.x_range), top = myDict[key][1],
                width = 0.2,source = source, color = "blue")
            glyph_count = glyph_count + 1

    fig.xaxis.major_label_orientation = pi/4 # puts dates in a / angle 
    fig.yaxis.axis_label = "Uses"
    fig.xaxis.axis_label = "Dates"
    fig.title.text = "Crosswalk and Road Usages Per Day"
    fig.title.align = "center" # also does left and right
    #fig.title.text_color = "orange"
    fig.title.text_font_size = "25px"

    print("\n\n\n")
    print(myDict)
    
    show(fig)
    return;

#This code needs some MAJOR refactoring
def bokeh_heat_map(db_cursor):
    query2 = "select count(distinct PERMAID), DATE_FORMAT(DATE, '%Y-%m-%d %a') as day, DATE_FORMAT(DATE, '%H') as hour from Contains where PERMAID in (select PERMAID from Person where USECROSSWALK=1 intersect select distinct PERMAID from Contains) group by hour,day order by day, hour;"
    db_cursor.execute(query2)
    heatmap_raw = db_cursor.fetchall() #(crosswalk uses, day, hour)

    readable_hours = ["8am", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm"]

    #format results    
    counts = []
    sub_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    length = len(readable_hours)
    hours = []
    days = []
    day_range = []
    last_date = None

    for result in heatmap_raw:
        current_date = datetime.strptime(result[1], '%Y-%m-%d %a')
        last_result = result

        if last_date != None and last_date != current_date:
            last_str_day = last_date.strftime('%Y-%m-%d %a')
            sub_day += ([last_str_day] * length)
            counts += sub_counts
            days += sub_day
            hours += readable_hours
            sub_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        #inserts a row of 0s for every hour for missing days
        while last_date != None and (current_date - last_date).days > 1:
            sub_day = []
            last_date = last_date + timedelta(days=1)
            last_str_day = last_date.strftime('%Y-%m-%d %a')
            #if last_str_day not in day_range:
            day_range.append(last_str_day)
            counts += [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            hours += readable_hours
            sub_day += ([last_str_day] * length)
            days += sub_day

        sub_day = []
        hour = int(result[2])
        sub_counts[hour-13] = result[0]
        str_day = result[1]

        if str_day not in day_range:
            day_range.append(str_day)

        last_date = current_date

    #append the last day
    hours += readable_hours
    counts += sub_counts
    str_day = current_date.strftime('%Y-%m-%d %a')
    days += [str_day] * length

    data = {
        'Day': days,
        'Hour': hours,
        'Count': counts
    }

    df = pd.DataFrame(data)
    TOOLS = "pan,box_zoom,reset,wheel_zoom"
    p = figure(title="Crosswalk Uses Per Day from {0} to {1}".format(day_range[0], day_range[-1]), 
                x_range=day_range, y_range=readable_hours, width=1024, height=600, tools=TOOLS, toolbar_location="below")
    p.yaxis.axis_label = "Hour"
    p.xaxis.axis_label = "Day"
    p.xaxis.major_label_orientation = pi / 4 #rotate 45 degrees
    p.title.text_font_size = "25px"
    p.title.align = "center" # also does left and right
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None

    mapper = LinearColorMapper(palette=['#ffffe5','#fff7bc','#fee391','#fec44f','#fe9929','#ec7014','#cc4c02','#993404','#662506'], low=0, high=np.max(counts))
    color_bar = ColorBar(title="Frequency", color_mapper=mapper, major_label_text_font_size="7px",
                     ticker=BasicTicker(desired_num_ticks=3),
                     formatter=PrintfTickFormatter(format="%d"),
                     label_standoff=6, border_line_color=None)

    hm = p.rect(x="Day", y="Hour", source=df, width = 1, height=1,
                 fill_color={'field': 'Count', 'transform': mapper}, line_color=None)
    p.add_layout(color_bar, 'right')
    print(json.dumps(json_item(p, "heatmap")))

    return
    
def main():
    connection = server_info.connect_to_database()
    db_cursor = connection.cursor()
    #NOTE this script only produces one plot at a time because it sets up its own html page - IT IS ONLY FOR TESTING AND THEN CAN BE IMPLEMENTED INTO EMBEDDING
    #bokeh_single_bar_graph(db_cursor) # WORKS CORRECTLY
    #bokeh_double_bar_graph(db_cursor) # DOES NOT WORK CORRECTLY
    #bokeh_double_line_graph(db_cursor) # WORKS CORRECTLY
    #bokeh_double_scatter_plot(db_cursor) # WORKS CORRECTLY - LOOKS ODD
    #bokeh_heat_map(db_cursor)
    db_cursor.close()
    connection.close()

if __name__ == '__main__':
    main()
