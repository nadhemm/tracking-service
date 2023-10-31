from unittest.mock import patch

import responses
from flask import current_app

from app import app
from app.models import db
from app.models.tracking import Tracking, TrackingState
from app.services.tracking import process_tracking_service
from app.tests.factories import TrackingFactory
from app.tests.config import test_client, requests_mock


@patch("app.services.tracking.trigger_process_tracking_async")
def test_process_tracking_should_store_data_and_trigger_async_processing(trigger_process_tracking_async, test_client):
    request_body = {
        "parcel_delivery_id": 123,
        "parcel_carrier_name": "La Poste",
        "parcel_full_address": {
            "postcode": "93400",
            "country": "Germany",
        },
    }
    response = test_client.post(
        "rest/trackings/",
        json=request_body,
        headers={'Client-Id': 'MOEZ'}
    )
    assert response.status_code == 200

    assert len(Tracking.query.all()) == 1
    tracking = Tracking.query.one()
    assert tracking.payload == request_body

    trigger_process_tracking_async.assert_called_once()


def test_process_tracking_with_invalid_input_should_fail_before_triggering_async_task(test_client):
    # data format is wrong/missing
    request_body = {
        "parcel_delivery_id": 123,
        "parcel_carrier_name": "La Poste",
        "parcel_full_address": {
            "postcode": "93400",
        },
    }

    response = test_client.post("rest/trackings/", json=request_body, headers={'Client-Id':'MOEZ'})
    assert response.status_code == 400
    assert "1 validation error for InputSchema" in response.text
    assert "Field required [type=missing, input_value={'postcode': '93400'}, input_type=dict]" in response.text



@patch("app.services.tracking.trigger_process_tracking_async")
def test_process_tracking_through_file(trigger_process_tracking_async, test_client):
    # We assume that file was already uploaded to this location using SFTP server
    file_path = 'tests/test_data/dummy_data_nadhem_gmbh.csv'
    response = test_client.post(
        "rest/trackings/file_based",
        json={"file_path": file_path},
        headers={'Client-Id':'NADHEM'}
    )
    assert response.status_code == 200
    assert trigger_process_tracking_async.call_count == 3
    assert len(Tracking.query.all()) == 3


def test_process_tracking_async_task(test_client, requests_mock):
    request_body = {
        "parcel_delivery_id": 123,
        "parcel_carrier_name": "La Poste",
        "parcel_full_address": {
            "postcode": "93400",
            "country": "Germany",
        },
    }
    # tracking created in previous task
    tracking = TrackingFactory(payload=request_body, client_id="MOEZ")

    # mock parcellab response
    requests_mock.add(
        responses.POST,
        f"{current_app.config['PARCELLAB_URL']}/track",
        status=200,
        json={
            "receivedAt": '2030-01-01T16:12:00.000Z',
            "validation": {
                "hasAllRequiredKeys": True,
            },
            "payload": [
                {
                }
            ]
        },
    )

    # this should: transform the data, send it to parcellab and update tracking state
    process_tracking_service(tracking_id=tracking.id)
    db.session.refresh(tracking)

    # assert data transformed correctly
    assert tracking.courier == 'colissimo'
    assert tracking.destination_country_iso3 == 'DEU'
    assert tracking.zip_code == '93400'
    assert tracking.tracking_number == '123'
    assert tracking.state == TrackingState.SENT

    # parcellab REST call fired
    assert requests_mock.assert_all_requests_are_fired
