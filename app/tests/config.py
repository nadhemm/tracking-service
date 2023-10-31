import pytest
from responses import RequestsMock

from app import create_app
from app.models import db


@pytest.fixture(scope='function', autouse=True)
def test_client():
    flask_app = create_app("test")

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()
            db.session.commit()


@pytest.fixture(scope="function", autouse=True)
def requests_mock():
    with RequestsMock(assert_all_requests_are_fired=True) as requests_mock_obj:
        yield requests_mock_obj
