from pydantic import BaseModel, ValidationError

from app.errors import InvalidInputData
from app.models.tracking import Tracking, TrackingState

COUNTRY_TO_ISO3 = {
    # TODO: use full list or use see: https://pypi.org/project/iso3166/
    "Germany": "DEU",
    "France": "FRA"
}

CARRIER_NAME_TO_KEY = {
    "La Poste": "colissimo",
    "DHL Global Mail": "dhl - gm",
    "DHL": "dhl - germany, dhl - benelux",
    "DPD": "dpd - de",
    "FedEx": "fedex",
    "GLS Germany / France / Denmark": "gls",
    "Mondial Relay": "mondial",
    "Royal Mail": "royalmail",
    "UPS Mail": "ups - mi",
}


class BaseTransformer:
    tracking: Tracking
    input_schema: BaseModel

    def __init__(self, tracking: Tracking):
        self.tracking = tracking

    @classmethod
    def validate_input_data(cls, json):
        try:
            cls.input_schema(**json)
        except ValidationError as e:
            # TODO: send to reporting channel or return 400 status code..
            raise InvalidInputData(e)

    def transform(self):
        self._transform()
        self.tracking.update_state(TrackingState.TRANSFORMED)

    def _transform(self):
        # Method to be implemented in child classes
        raise NotImplementedError
