from app.models import db
from app.transformers.base_transformer import BaseTransformer, CARRIER_NAME_TO_KEY, COUNTRY_TO_ISO3
from pydantic import BaseModel


class InputSchema(BaseModel):
    trackID: int
    courrier: str
    postalCode: str
    country: str


class NadhemGmbhTransformer(BaseTransformer):
    """ Custom transformer handling input data from client: Nadhem Gmbh """
    input_schema = InputSchema

    def _transform(self):
        data = self.tracking.payload
        self.tracking.tracking_number = data['trackID']
        self.tracking.courier = CARRIER_NAME_TO_KEY[data['courrier']]
        self.tracking.zip_code = data['postalCode']
        self.tracking.destination_country_iso3 = COUNTRY_TO_ISO3[data['country']]

        db.session.add(self.tracking)
        db.session.commit()
