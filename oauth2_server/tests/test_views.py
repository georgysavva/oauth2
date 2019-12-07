import jwt
import pytest
from freezegun import freeze_time
from unittest import mock


def issue_token_valid_request_data():
    return {
        'client_id': '1234',
        'client_secret': 'qwerty',
        'username': 'bob',
        'password': 'pass',
        'grant_type': 'password'
    }


@freeze_time("2019-12-06 01:00:00")
def test_issue_token_and_get_token_info_smoke(flask_client):
    resp = flask_client.post('/v1/token', json=issue_token_valid_request_data())
    assert resp.status_code == 200
    assert resp.json == {
        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJib2IiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjUwMDEvdjEvdG9rZW4iLCJjaWQiOiIxMjM0IiwiaWF0IjoxNTc1NTk0MDAwLCJleHAiOjE1NzU1OTQwMDUsInNjb3BlIjoiY3VycmVudF90aW1lIGVwb2NoX3RpbWUifQ.Ncs1HU4nbO7nYr1U9WCA59VsBMzF4qrcHc0BzLwsLIE'
    }
    token = resp.json['access_token']
    resp = flask_client.get('/v1/token', json={'access_token': token})
    assert resp.status_code == 200
    assert resp.json == {
        'client_id': '1234',
        'user_id': 'bob',
        'issuer_url': 'http://localhost:5001/v1/token',
        'issued_at': 1575594000,
        'expires_at': 1575594005,
        'scope': ['current_time', 'epoch_time']

    }


@pytest.mark.parametrize('missing_field',
                         ['client_id', 'client_secret', 'username', 'password', 'grant_type'])
def test_issue_token_request_validation(flask_client, missing_field):
    request_data = issue_token_valid_request_data()
    request_data.pop(missing_field)
    resp = flask_client.post('/v1/token', json=request_data)
    assert resp.status_code == 400
    assert resp.json == {
        'error': 'invalid_request',
        'error_description': mock.ANY,
    }


def test_invalid_grant_type(flask_client):
    request_data = issue_token_valid_request_data()
    request_data['grant_type'] = 'foo'
    resp = flask_client.post('/v1/token', json=request_data)
    assert resp.status_code == 400
    assert resp.json == {
        'error': 'invalid_request',
        'error_description': mock.ANY,
    }


def test_unsupported_grant_type(flask_client):
    request_data = issue_token_valid_request_data()
    request_data['grant_type'] = 'code'
    resp = flask_client.post('/v1/token', json=request_data)
    assert resp.status_code == 400
    assert resp.json == {
        'error': 'unsupported_grant_type',
        'error_description': "Unsupported grant type. Server only supports 'password' grant type.",
    }


def test_application_not_found(flask_client):
    request_data = issue_token_valid_request_data()
    request_data['client_id'] = '3333'
    resp = flask_client.post('/v1/token', json=request_data)
    assert resp.status_code == 400
    assert resp.json == {
        'error': 'invalid_client',
        'error_description': "Client with id '3333' not found "
                             "or pair client_id and client_secret does not match",
    }


def test_application_client_id_and_secret_dont_match(flask_client):
    request_data = issue_token_valid_request_data()
    request_data['client_secret'] = 'ytrewq'
    resp = flask_client.post('/v1/token', json=request_data)
    assert resp.status_code == 400
    assert resp.json == {
        'error': 'invalid_client',
        'error_description': "Client with id '1234' not found "
                             "or pair client_id and client_secret does not match",
    }


def test_get_token_info_request_validation(flask_client):
    resp = flask_client.get('/v1/token', json={'token': 'fooo'})
    assert resp.status_code == 400
    assert resp.json == {
        'error': 'invalid_request',
        'error_description': mock.ANY
    }


def test_access_token_invalid(flask_client):
    resp = flask_client.get('/v1/token', json={'access_token': 'fooo'})
    assert resp.status_code == 401
    assert resp.json == {
        'error': 'invalid_access_token',
        'error_description': "Access token is invalid"
    }


def test_access_token_expired(flask_client):
    with freeze_time("2019-12-06 01:00:00"):
        resp = flask_client.post('/v1/token', json=issue_token_valid_request_data())
    assert resp.status_code == 200
    assert resp.json == {
        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJib2IiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjUwMDEvdjEvdG9rZW4iLCJjaWQiOiIxMjM0IiwiaWF0IjoxNTc1NTk0MDAwLCJleHAiOjE1NzU1OTQwMDUsInNjb3BlIjoiY3VycmVudF90aW1lIGVwb2NoX3RpbWUifQ.Ncs1HU4nbO7nYr1U9WCA59VsBMzF4qrcHc0BzLwsLIE'
    }
    token = resp.json['access_token']
    with freeze_time("2019-12-06 02:00:00"):
        resp = flask_client.get('/v1/token', json={'access_token': token})
    assert resp.status_code == 401
    assert resp.json == {
        'error': 'access_token_expired',
        'error_description': "Access token has expired"
    }


@pytest.mark.parametrize('missing_field', ['sub', 'iss', 'cid', 'iat', 'exp', 'scope'])
def test_jwt_fields_missing(flask_client, caplog, missing_field):
    jwt_payload = {
        'sub': 'bob',
        'iss': 'http://localhost:5001/v1/token',
        'cid': '1234',
        'iat': 1575594000,
        'exp': 1575594005,
        'scope': 'current_time',
    }
    jwt_payload.pop(missing_field)
    token = jwt.encode(
        jwt_payload, '604fe435c2a4d63046741c572023c448b76af554c824a2065d53563fac168cd8', 'HS256'
    ).decode()

    with freeze_time("2019-12-06 01:00:00"):
        resp = flask_client.get('/v1/token', json={'access_token': token})
    assert "JWT payload does not contain all required fields with proper types" in caplog.messages
    assert resp.status_code == 401
    assert resp.json == {
        'error': 'invalid_access_token',
        'error_description': "Access token is invalid"
    }
