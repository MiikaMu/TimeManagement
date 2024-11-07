import psycopg2
from psycopg2.extras import RealDictCursor
from .config import config
import json

def db_create_time(startTime, endTime, lunchBreak, consultName, customerName):
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        SQL = 'INSERT INTO timemanagement (starttime, endtime, lunchbreak, consultantname, customername) VALUES (%s, %s, %s, %s, %s);'
        cursor.execute(SQL, (startTime, endTime, lunchBreak, consultName, customerName))
        con.commit()
        result = {"Success": "Working hours submitted for: %s " % consultName}
        cursor.close()
        return json.dumps(result)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

def db_get_time():
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        SQL = 'SELECT * FROM timemanagement;'
        cursor.execute(SQL)
        data = cursor.fetchall()
        cursor.close()
        return json.dumps({"Submitted hours": data})
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

if __name__ == '__main__':
    print(db_get_time())