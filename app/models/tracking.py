from enum import Enum

from app.models import db
from sqlalchemy import JSON


class TrackingState(str, Enum):
    CREATED = 'CREATED'
    TRANSFORMED = 'TRANSFORMED'
    SENT = 'SENT'


class Tracking(db.Model):
    __tablename__ = "tracking"

    id = db.Column(db.Integer, primary_key=True)
    courier = db.Column(db.String(256))
    tracking_number = db.Column(db.String(256))
    zip_code = db.Column(db.String(6))
    destination_country_iso3 = db.Column(db.String(10))

    payload = db.Column(JSON)
    client_id = db.Column(db.String(256))
    state = db.Column(db.Enum(TrackingState), server_default='CREATED')

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).one_or_none()

    def update_state(self, state: TrackingState):
        self.state = state
        db.session.add(self)
        db.session.commit()

    def to_parcellab_input_dict(self)-> dict:
        return {
            field:v for field, v in self.__dict__.items() if field in
            {'courier', 'tracking_number', 'zip_code', 'destination_country_iso3'}
        }
