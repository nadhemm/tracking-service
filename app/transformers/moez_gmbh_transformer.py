from app.models import db
from app.transformers.base_transformer import BaseTransformer, CARRIER_NAME_TO_KEY, COUNTRY_TO_ISO3
from pydantic import BaseModel


class AddressInput(BaseModel):
    postcode: str
    country: str


class InputSchema(BaseModel):
    parcel_delivery_id: int
    parcel_carrier_name: str
    parcel_full_address: AddressInput


class MoezGmbhTransformer(BaseTransformer):
    """ Custom transformer handling input data from the client: Moez Gmbh """
    input_schema = InputSchema

    def _transform(self):
        data = self.tracking.payload
        self.tracking.courier = CARRIER_NAME_TO_KEY[data['parcel_carrier_name']]
        self.tracking.tracking_number = data['parcel_delivery_id']
        address = data['parcel_full_address']
        self.tracking.zip_code = address['postcode']
        self.tracking.destination_country_iso3 = COUNTRY_TO_ISO3[address['country']]

        db.session.add(self.tracking)
        db.session.commit()
