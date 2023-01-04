#!/bin/bash
import sys
import server_info

import json
from SageBokeh import bokeh_heat_map
from SageBokeh import bokeh_double_line_graph
from SageBokeh import bokeh_double_scatter_plot
from SageBokeh import bokeh_direction_scatter_plot

def most_recent_day():
    #connect to db
    connection = server_info.connect_to_database()
    db_cursor = connection.cursor()

    #create charts
    bokeh_heat_map(db_cursor)
    print("***")
    bokeh_double_line_graph(db_cursor)
    print("***")
    #bokeh_double_scatter_plot(db_cursor)
    bokeh_direction_scatter_plot(db_cursor)

    db_cursor.close()
    connection.close()

if __name__ == '__main__':
    most_recent_day()
