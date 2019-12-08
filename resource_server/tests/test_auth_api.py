from unittest import mock

import pytest

from apis import IncorrectResponseError
from apis.auth import AuthAPI


def test_validate_token_info_response_smoke():
    response = mock.Mock()
    response_json = {
        'user_id': 'bob',
        'scope': ['current_time', 'epoch_time']
    }
    result = AuthAPI.validate_token_info_response(response, response_json)
    assert result == ('bob', ['current_time', 'epoch_time'])


def test_validate_token_info_response_empty_scope():
    response = mock.Mock()
    response_json = {
        'user_id': 'bob',
        'scope': []
    }
    result = AuthAPI.validate_token_info_response(response, response_json)
    assert result == ('bob', [])


def test_validate_token_info_response_user_id_missing():
    response = mock.Mock()
    response_json = {
        'scope': ['current_time', 'epoch_time']
    }
    with pytest.raises(IncorrectResponseError) as exc_info:
        AuthAPI.validate_token_info_response(response, response_json)
    assert str(exc_info.value) == "'user_id' field is missing or wrong type"


def test_validate_token_info_response_user_id_wrong_type():
    response = mock.Mock()
    response_json = {
        'user_id': 100,
        'scope': ['current_time', 'epoch_time']
    }
    with pytest.raises(IncorrectResponseError) as exc_info:
        AuthAPI.validate_token_info_response(response, response_json)
    assert str(exc_info.value) == "'user_id' field is missing or wrong type"


def test_validate_token_info_response_scope_missing():
    response = mock.Mock()
    response_json = {
        'user_id': 'bob',
    }
    with pytest.raises(IncorrectResponseError) as exc_info:
        AuthAPI.validate_token_info_response(response, response_json)
    assert str(exc_info.value) == "'scope' field is missing or wrong type"


def test_validate_token_info_response_scope_wrong_type():
    response = mock.Mock()
    response_json = {
        'user_id': 'bob',
        'scope': "current_time epoch_time"
    }
    with pytest.raises(IncorrectResponseError) as exc_info:
        AuthAPI.validate_token_info_response(response, response_json)
    assert str(exc_info.value) == "'scope' field is missing or wrong type"


@pytest.mark.parametrize('scope', [
    "current_time epoch_time",
    ['current_time', 1],
    [1, 2]
])
def test_validate_token_info_response_scope_wrong_type(scope):
    response = mock.Mock()
    response_json = {
        'user_id': 'bob',
        'scope': scope
    }
    with pytest.raises(IncorrectResponseError) as exc_info:
        AuthAPI.validate_token_info_response(response, response_json)
    assert str(exc_info.value) == "'scope' field is missing or wrong type"
