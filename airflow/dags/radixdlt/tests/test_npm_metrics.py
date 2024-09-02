import pytest
from unittest.mock import patch, MagicMock
from requests.models import Response
from sqlalchemy.exc import SQLAlchemyError

from radixdlt.models.npm.npm_model import NpmMetricsModel


@pytest.fixture
def mock_get_session():
    with patch("radixdlt.models.npm.npm_model.get_session") as mock:
        yield mock


@pytest.fixture
def mock_requests_get():
    with patch("radixdlt.models.npm.npm_model.requests.get") as mock:
        yield mock


def test_fetch_and_save_data_success(mock_requests_get, mock_get_session):
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.json.return_value = {"downloads": 1000}
    mock_requests_get.return_value = response

    session_mock = MagicMock()
    mock_get_session.return_value.__enter__.return_value = session_mock

    NpmMetricsModel.fetch_and_save_data("some_package")

    session_mock.add.assert_called_once()
    session_mock.commit.assert_called_once()
    session_mock.close.assert_called_once()


def test_fetch_and_save_data_api_failure(mock_requests_get):
    response = MagicMock(spec=Response)
    response.status_code = 404
    mock_requests_get.return_value = response

    with pytest.raises(Exception):
        NpmMetricsModel.fetch_and_save_data("some_package")


def test_fetch_and_save_data_db_failure(mock_requests_get, mock_get_session):
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.json.return_value = {"downloads": 1000}
    mock_requests_get.return_value = response

    session_mock = MagicMock()
    session_mock.add.side_effect = SQLAlchemyError("DB Error")
    mock_get_session.return_value.__enter__.return_value = session_mock

    with pytest.raises(SQLAlchemyError):
        NpmMetricsModel.fetch_and_save_data("some_package")

    session_mock.rollback.assert_called_once()
    session_mock.close.assert_called_once()
