import pytest
import requests
import requests_mock
from freezegun import freeze_time

import apis.auth

valid_access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJib2IiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjUwMDEvdjEvdG9rZW4iLCJjaWQiOiIxMjM0IiwiaWF0IjoxNTc1NTk0MDAwLCJleHAiOjE1NzU1OTQwMDUsInNjb3BlIjoiY3VycmVudF90aW1lIGVwb2NoX3RpbWUifQ.Ncs1HU4nbO7nYr1U9WCA59VsBMzF4qrcHc0BzLwsLIE'  # noqa


@pytest.mark.parametrize(
    'time_resource_name,result', [
        ('current_time', '2019-12-06T01:00:01+00:00'),
        ('epoch_time', 1575594001)
    ])
@freeze_time("2019-12-06T01:00:01+00:00")
def test_get_current_time_and_epoch_time_smoke(flask_client, time_resource_name, result):
    def _get_token_info_http_request_matcher(request):
        return request.json() == {'access_token': valid_access_token}

    with requests_mock.Mocker() as m:
        m.get(
            'http://oauth2-server:8000/v1/token',
            additional_matcher=_get_token_info_http_request_matcher,
            json={
                'client_id': '1234',
                'user_id': 'bob',
                'issuer_url': 'http://oauth2-server:8000/v1/token',
                'issued_at': 1575594000,
                'expires_at': 1575594005,
                'scope': ['current_time', 'epoch_time']
            }
        )
        resp = flask_client.get(
            f'/v1/{time_resource_name}',
            headers={'Authorization': f'Bearer {valid_access_token}'}
        )
    assert resp.status_code == 200
    assert resp.json == {time_resource_name: result}


@pytest.fixture(params=['current_time', 'epoch_time'])
def time_resource_name(request):
    return request.param


def test_authorization_header_missing(flask_client, time_resource_name):
    resp = flask_client.get(f'/v1/{time_resource_name}', headers={})
    assert resp.status_code == 400
    assert resp.json == {
        'error': 'invalid_request',
        'error_description': "Authorization header is missing"
    }


def test_authorization_header_incorrect_format(flask_client, time_resource_name):
    resp = flask_client.get(f'/v1/{time_resource_name}', headers={'Authorization': 'foo'})
    assert resp.status_code == 400
    assert resp.json == {
        'error': 'invalid_request',
        'error_description': "Authorization header has incorrect format, "
                             "it must start with 'Bearer': foo"
    }


@pytest.mark.parametrize(
    'error_code,error_description,status_code', [
        ('invalid_access_token', "Access token is invalid", 401),
        ('access_token_expired', "Access token has expired", 401),
    ])
def test_get_token_info_response_error_code_expected(flask_client, time_resource_name, error_code,
                                                     error_description, status_code):
    with requests_mock.Mocker() as m:
        m.get(
            'http://oauth2-server:8000/v1/token', status_code=status_code,
            json={
                'error': error_code,
                'error_description': error_description
            }
        )
        resp = flask_client.get(
            f'/v1/{time_resource_name}',
            headers={'Authorization': f'Bearer {valid_access_token}'}
        )

    assert resp.json == {
        'error': error_code,
        'error_description': error_description
    }
    assert resp.status_code == status_code


def test_get_token_info_response_error_code_invalid_request(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.get(
            'http://oauth2-server:8000/v1/token', status_code=400,
            json={
                'error': 'invalid_request',
                'error_description': "Something wrong with your request"
            }
        )
        with pytest.raises(apis.InvalidRequestError) as exc_info:
            flask_client.get(
                f'/v1/{time_resource_name}',
                headers={'Authorization': f'Bearer {valid_access_token}'}
            )

    assert str(exc_info.value) == "Something wrong with your request"


def test_get_token_info_response_error_http_status_code(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.get(
            'http://oauth2-server:8000/v1/token', status_code=500, reason='Internal error'
        )
        with pytest.raises(requests.HTTPError) as exc_info:
            flask_client.get(
                f'/v1/{time_resource_name}',
                headers={'Authorization': f'Bearer {valid_access_token}'}
            )

    assert str(exc_info.value) == ("500 Server Error: "
                                   "Internal error for url: http://oauth2-server:8000/v1/token")


def test_get_token_info_response_empty_json_body(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.get('http://oauth2-server:8000/v1/token', text='Success')
        with pytest.raises(apis.IncorrectResponseError) as exc_info:
            flask_client.get(
                f'/v1/{time_resource_name}',
                headers={'Authorization': f'Bearer {valid_access_token}'}
            )

    assert str(exc_info.value) == "Empty json body"


def test_get_token_info_response_incorrect_json_body(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.get('http://oauth2-server:8000/v1/token', json={'user_id': 'bob'})
        with pytest.raises(apis.IncorrectResponseError) as exc_info:
            flask_client.get(
                f'/v1/{time_resource_name}',
                headers={'Authorization': f'Bearer {valid_access_token}'}
            )

    assert str(exc_info.value) == "'scope' field is missing or wrong type"


def test_time_resource_permission_denied(flask_client, time_resource_name):
    token_info = {
        'user_id': 'bob',
        'scope': ['current_time', 'epoch_time']
    }
    token_info['scope'].remove(time_resource_name)
    with requests_mock.Mocker() as m:
        m.get('http://oauth2-server:8000/v1/token', json=token_info)
        resp = flask_client.get(
            f'/v1/{time_resource_name}',
            headers={'Authorization': f'Bearer {valid_access_token}'}
        )

    assert resp.json == {
        'error': 'permission_denied',
        'error_description': f"Access to resource {time_resource_name} denied, "
        f"out of the token scope"
    }
    assert resp.status_code == 403
