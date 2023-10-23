import factory
from sqlalchemy.orm import scoped_session

from app.models import db
from app.models.tracking import Tracking

session_factory = scoped_session(lambda: db.session, scopefunc=lambda: db.session)


class TrackingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Tracking
        sqlalchemy_session = session_factory
        sqlalchemy_session_persistence = "commit"


    id = 1
    tracking_number = factory.Faker("lexify")
    zip_code = factory.Faker("bothify", text="#####")
    destination_country_iso3 = factory.Faker("lexify", text="??????????")