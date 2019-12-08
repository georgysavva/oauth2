import pytest
import requests
import requests_mock

from apis import exceptions


def issue_token_valid_request_data():
    return {
        'client_id': '1234',
        'client_secret': 'qwerty',
        'username': 'bob',
        'password': 'pass',
        'grant_type': 'password'
    }


valid_access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJib2IiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjUwMDEvdjEvdG9rZW4iLCJjaWQiOiIxMjM0IiwiaWF0IjoxNTc1NTk0MDAwLCJleHAiOjE1NzU1OTQwMDUsInNjb3BlIjoiY3VycmVudF90aW1lIGVwb2NoX3RpbWUifQ.Ncs1HU4nbO7nYr1U9WCA59VsBMzF4qrcHc0BzLwsLIE'  # noqa


@pytest.mark.parametrize(
    'time_resource_name,result', [
        ('current_time', '2019-12-06T01:00:01+00:00'),
        ('epoch_time', 1575594001)
    ])
def test_get_current_time_and_epoch_smoke(flask_client, time_resource_name, result):
    def _issue_token_http_request_matcher(request):
        return request.json() == {
            'grant_type': 'password',
            'client_id': '1234',
            'client_secret': 'qwert',
            'username': 'bob',
            'password': 'bob-pass'
        }

    with requests_mock.Mocker() as m:
        m.post(
            'http://localhost:5001/v1/token',
            additional_matcher=_issue_token_http_request_matcher,
            json={'access_token': valid_access_token}
        )
        m.get(
            f'http://localhost:5002/v1/{time_resource_name}',
            request_headers={'Authorization': f'Bearer {valid_access_token}'},
            json={time_resource_name: result}
        )
        resp = flask_client.get(f'/{time_resource_name}')
    assert resp.status_code == 200
    assert resp.data.decode() == str(result)


@pytest.fixture(params=['current_time', 'epoch_time'])
def time_resource_name(request):
    return request.param


def test_issue_token_response_error_code_invalid_request(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.post(
            'http://localhost:5001/v1/token', status_code=400,
            json={
                'error': 'invalid_request',
                'error_description': "Something wrong with your request"
            }
        )
        with pytest.raises(exceptions.InvalidRequestError) as exc_info:
            flask_client.get(f'/{time_resource_name}')
    assert str(exc_info.value) == "Something wrong with your request"


def test_issue_token_response_error_http_status_code(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.post(
            'http://localhost:5001/v1/token', status_code=500, reason='Internal error'
        )
        with pytest.raises(requests.HTTPError) as exc_info:
            flask_client.get(f'/{time_resource_name}')

    assert str(exc_info.value) == ("500 Server Error: "
                                   "Internal error for url: http://localhost:5001/v1/token")


def test_issue_token_response_empty_json_body(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', text='Success')
        with pytest.raises(exceptions.IncorrectResponseError) as exc_info:
            flask_client.get(f'/{time_resource_name}')
    assert str(exc_info.value) == "Empty json body"


def test_issue_token_response_access_token_field_missing(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', json={'token': 'some-token'})
        with pytest.raises(exceptions.IncorrectResponseError) as exc_info:
            flask_client.get(f'/{time_resource_name}')
    assert str(exc_info.value) == "'access_token' field is missing or wrong type"


def test_issue_token_response_access_token_field_wrong_type(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', json={'access_token': 12345})
        with pytest.raises(exceptions.IncorrectResponseError) as exc_info:
            flask_client.get(f'/{time_resource_name}')
    assert str(exc_info.value) == "'access_token' field is missing or wrong type"


@pytest.mark.parametrize(
    'error_code,error_description,status_code', [
        ('invalid_access_token', "Access token is invalid", 401),
        ('access_token_expired', "Access token has expired", 401),
        ('permission_denied', "Access to resource denied, out of the token scope", 403)
    ])
def test_time_resource_response_error_code_expected(flask_client, time_resource_name, error_code,
                                                    error_description, status_code):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', json={'access_token': valid_access_token})
        m.get(
            f'http://localhost:5002/v1/{time_resource_name}', status_code=status_code,
            request_headers={'Authorization': f'Bearer {valid_access_token}'},
            json={
                'error': error_code,
                'error_description': error_description
            }
        )
        resp = flask_client.get(f'/{time_resource_name}')
    assert resp.data.decode() == error_description
    assert resp.status_code == status_code


def test_time_resource_response_error_code_invalid_request(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', json={'access_token': valid_access_token})
        m.get(
            f'http://localhost:5002/v1/{time_resource_name}', status_code=400,
            request_headers={'Authorization': f'Bearer {valid_access_token}'},
            json={
                'error': 'invalid_request',
                'error_description': "Something wrong with your request"
            }
        )
        with pytest.raises(exceptions.InvalidRequestError) as exc_info:
            flask_client.get(f'/{time_resource_name}')
    assert str(exc_info.value) == "Something wrong with your request"


def test_time_resource_response_error_http_status_code(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', json={'access_token': valid_access_token})
        m.get(
            f'http://localhost:5002/v1/{time_resource_name}', status_code=500,
            request_headers={'Authorization': f'Bearer {valid_access_token}'},
            reason="Internal error"
        )
        with pytest.raises(requests.HTTPError) as exc_info:
            flask_client.get(f'/{time_resource_name}')

    assert str(exc_info.value) == (
        f"500 Server Error: Internal error for url: http://localhost:5002/v1/{time_resource_name}"
    )


def test_time_resource_response_empty_json_body(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', json={'access_token': valid_access_token})
        m.get(
            f'http://localhost:5002/v1/{time_resource_name}',
            request_headers={'Authorization': f'Bearer {valid_access_token}'},
            text="Success"
        )
        with pytest.raises(exceptions.IncorrectResponseError) as exc_info:
            flask_client.get(f'/{time_resource_name}')
    assert str(exc_info.value) == "Empty json body"


def test_time_resource_response_time_field_missing(flask_client, time_resource_name):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', json={'access_token': valid_access_token})
        m.get(
            f'http://localhost:5002/v1/{time_resource_name}',
            request_headers={'Authorization': f'Bearer {valid_access_token}'},
            json={'foo': '3'}
        )
        with pytest.raises(exceptions.IncorrectResponseError) as exc_info:
            flask_client.get(f'/{time_resource_name}')
    assert str(exc_info.value) == f"'{time_resource_name}' field is missing or wrong type"


def test_current_time_response_wrong_field_type(flask_client):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', json={'access_token': valid_access_token})
        m.get(
            'http://localhost:5002/v1/current_time',
            request_headers={'Authorization': f'Bearer {valid_access_token}'},
            json={'current_time': 1575594001}
        )
        with pytest.raises(exceptions.IncorrectResponseError) as exc_info:
            flask_client.get('/current_time')
    assert str(exc_info.value) == f"'current_time' field is missing or wrong type"


def test_epoch_time_response_wrong_field_type(flask_client):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:5001/v1/token', json={'access_token': valid_access_token})
        m.get(
            'http://localhost:5002/v1/epoch_time',
            request_headers={'Authorization': f'Bearer {valid_access_token}'},
            json={'epoch_time': '2019-12-06T01:00:01+00:00'}
        )
        with pytest.raises(exceptions.IncorrectResponseError) as exc_info:
            flask_client.get('/epoch_time')
    assert str(exc_info.value) == f"'epoch_time' field is missing or wrong type"
