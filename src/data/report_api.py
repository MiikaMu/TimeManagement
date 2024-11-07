from flask import Flask, request
from .report_service import *

app = Flask(__name__)

@app.route("/report", methods=['GET'])
def get_report():
    try:
        write_daily_report()
        return {"Success": "Daily report created and uploaded to Azure"}
    except:
        return {"Error": "Error while creating report"}
    
if __name__ == "__main__":
    app.run()