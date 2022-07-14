from datetime import datetime
import mysql.connector as mariadb
import sys
sys.path.insert(0, '/home/wesley/')
import server_info
import json

def main():
    query = "select distinct DATE_FORMAT(DATE, '%Y-%m-%d') from Frame;"
    formatted_array_of_dates = []
    connection = server_info.connect_to_database()
    db_cursor = connection.cursor()
    db_cursor.execute(str(query))

    record = db_cursor.fetchall()
    mystring = "testing"

    for item in record:
        bad_date = str(item)
        good_date = bad_date.strip('(')
        good_date = good_date.strip(')')
        good_date = good_date.strip(',')
        good_date = good_date.strip("'")
        formatted_array_of_dates.append(good_date)

    print(json.dumps(formatted_array_of_dates))

    db_cursor.close()
    connection.close()

if __name__ == '__main__':
    main()
