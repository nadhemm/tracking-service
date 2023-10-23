import csv

from flask import request

from app import celery
from app.clients import parcellab
from app.models.tracking import TrackingState
from app.transformers.moez_gmbh_transformer import MoezGmbhTransformer
from app.models import db
from app.models.tracking import Tracking
from app.transformers.base_transformer import BaseTransformer
from app.transformers.nadhem_gmbh_transformer import NadhemGmbhTransformer


def store_tracking_data_and_trigger_process_tracking_async(data: dict, client_id: str):
    tracking = _pre_process_tracking(data, client_id)
    trigger_process_tracking_async(tracking_id=tracking.id)
    return tracking


def _pre_process_tracking(data: dict, client_id: str):
    """ Store tracking data into tracking model, return ack to client and trigger async tracking processing """
    transformer: BaseTransformer = get_transformer(client_id)
    transformer.validate_input_data(data)
    tracking = Tracking(payload=data, client_id=client_id)
    db.session.add(tracking)
    db.session.commit()
    return tracking


def trigger_process_tracking_async(tracking_id: int):
    """ Call async function """
    process_tracking_task.delay(tracking_id)


@celery.task()
def process_tracking_task(tracking_id: int):
    """ Async function calling service """
    process_tracking_service(tracking_id)


def process_tracking_service(tracking_id: int):
    tracking = Tracking.get_by_id(tracking_id)

    # get correct transformer for current client
    transformer = get_transformer(tracking.client_id)

    # transform data into correct DataModel
    transformer(tracking).transform()

    # send data to parcellab
    parcellab.create_tracking(tracking)

    # update status
    tracking.update_state(TrackingState.SENT)


def get_transformer(client_id: str):
    """" Returns the correct transformer based on request header: client-id """
    client_id_to_transformer = {
     "NADHEM": NadhemGmbhTransformer,
     "MOEZ": MoezGmbhTransformer,
    }
    return client_id_to_transformer[client_id]


def process_trackings_by_file(file_path, client_id):
    # in the context of this poc, we'll assume we're using local paths
    with open(f"../{file_path}", 'r', newline="") as csv_file:
        # TODO: add support for other file types: json, fixed..
        csv_reader = csv.reader(csv_file)
        # Read and process the header row
        header = next(csv_reader)

        for input in csv_reader:
            store_tracking_data_and_trigger_process_tracking_async(dict(zip(header, input)), client_id)
