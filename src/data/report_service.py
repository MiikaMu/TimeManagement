import psycopg2
import json
import os
import uuid
from psycopg2.extras import RealDictCursor
from .config import config
from datetime import datetime
from azure.storage.blob import BlobClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

def db_get_time(today):
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        daily_query = """
        SELECT consultantName,
        DATE(startTime) AS day,
        customerName,
        SUM(EXTRACT(EPOCH FROM (endTime - startTime)) / 3600 - CASE WHEN lunchBreak THEN 0.5 ELSE 0 END) AS hours_worked
        FROM TimeManagement
        WHERE DATE(startTime) = %s
        GROUP BY consultantName, DATE(startTime), customerName
        ORDER BY consultantName, customerName;
        """

        customer_summary_query = """
        SELECT customerName,
        SUM(EXTRACT(EPOCH FROM (endTime - startTime)) / 3600 - CASE WHEN lunchBreak THEN 0.5 ELSE 0 END) AS total_hours
        FROM TimeManagement
        WHERE DATE(startTime) = %s
        GROUP BY customerName
        ORDER BY customerName;
        """
    
        cursor.execute(daily_query, (today,))
        daily_results = cursor.fetchall()
    
        cursor.execute(customer_summary_query, (today,))
        customer_summary = cursor.fetchall()

        cursor.close()
        return daily_results, customer_summary
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

def write_report(daily_data, customer_data):
    today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"time_report_{today}.txt"

    with open(filename, "w") as file:
        file.write(f"Time Tracking Report for {today}\n")
        file.write("="*50 + "\n\n")

        file.write("Daily Hours by Consultant:\n")
        file.write("-" * 28)
        current_consultant = None
        for row in daily_data:
            consultant = row['consultantname']
            customer = row['customername']
            hours = float(row['hours_worked'])

            if consultant != current_consultant:
                current_consultant = consultant
                file.write(f"\n{consultant}:\n")
            file.write(f"{customer}: {hours:.2f} hours\n")

        file.write("\n")
        file.write("*" * 50)
        file.write("\n")

        file.write("Total Hours by Customer:\n")
        file.write("-" * 25 + "\n")

        for row in customer_data:
            customer = row['customername']
            total_hours = float(row['total_hours'])
            file.write(f"{customer}: {total_hours:.2f} hours\n")

    print(f"Report written to {filename}")

    return filename

def send_blob(filename):

    CONNECTION_STRING = "<StorageAccountConnectionString>"
    CONTAINER_NAME = "testdata"
    BLOB_NAME = f"{filename}-{str(uuid.uuid4())[0:5]}.txt"
    LOCAL_FILE_PATH = f"/home/miika.mustamaki/flask-app/TimeManagement/src/data/{filename}"

    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    with open(LOCAL_FILE_PATH, "rb") as data:
        container_client.upload_blob(name=BLOB_NAME, data=data, overwrite=True)

    os.remove(LOCAL_FILE_PATH)

    print(f"File '{filename}' uploaded to Azure storage: '{BLOB_NAME}'.")

def write_daily_report():
    today = datetime.now().strftime('%Y-%m-%d')
    
    daily_data, customer_data = db_get_time(today)

    filename = write_report(daily_data, customer_data)
    
    send_blob(filename)

if __name__ == "__main__":
    write_daily_report()