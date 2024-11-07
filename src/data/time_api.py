from flask import Flask, request
from .time_service import *

app = Flask(__name__)

@app.route("/time", methods=['POST'])
def create_time():
    try: 
        datalist = request.get_json()

        for data in datalist:
            startTime = data['starttime']
            endTime = data['endtime']
            lunchBreak = data['lunchbreak']
            consultName = data['consultantname']
            customerName = data['customername']
            db_create_time(startTime, endTime, lunchBreak, consultName, customerName)
        return {"Success": "Hours submitted succesfully!"}
    except:
        return {"Error": "error submitting hours"}
    
if __name__ == "__main__":
    app.run()