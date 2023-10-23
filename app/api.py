import csv

from flask import Blueprint, request

from flask_cors import CORS

from app.services.tracking import store_tracking_data_and_trigger_process_tracking_async, process_trackings_by_file

rest = Blueprint("rest", __name__)

CORS(rest)


@rest.route('/trackings/', methods=['POST'])
def ep_process_tracking():
    tracking = store_tracking_data_and_trigger_process_tracking_async(request.json, client_id=request.headers.get('Client-id'))
    return f"All done : tracking object {tracking.id} has been created", 200


@rest.route('/trackings/file_based', methods=['POST'])
def ep_process_trackings_by_file():
    client_id = request.headers.get('Client-id')
    file_path = request.json['file_path']

    process_trackings_by_file(file_path, client_id)

    return "All done: tracking objects has been created", 200
