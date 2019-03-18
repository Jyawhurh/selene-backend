import json
import uuid
from http import HTTPStatus

from behave import when, then, given
from hamcrest import assert_that, equal_to, has_key, is_not


@when('try to fetch device\'s setting')
def get_device_settings(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers=dict(Authorization='Bearer {token}'.format(token=access_token))
    context.response_setting = context.client.get(
        '/v1/device/{uuid}/setting'.format(uuid=device_id),
        headers=headers
    )


@then('a valid setting should be returned')
def validate_response_setting(context):
    response = context.response_setting
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    setting = json.loads(response.data)
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    assert_that(setting, has_key('uuid'))
    assert_that(setting, has_key('systemUnit'))
    assert_that(setting, has_key('timeFormat'))
    assert_that(setting, has_key('dateFormat'))
    assert_that(setting, has_key('ttsSettings'))


@when('the settings endpoint is a called to a not allowed device')
def get_device_settings(context):
    access_token = context.device_login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.get_invalid_setting_response = context.client.get(
        '/v1/device/{uuid}/setting'.format(uuid=str(uuid.uuid4())),
        headers=headers
    )


@then('a 401 status code should be returned for the setting')
def validate_response(context):
    response = context.get_invalid_setting_response
    assert_that(response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))


@given('a device\'s setting with a valid etag')
def get_device_setting_etag(context):
    access_token = context.device_login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    device_id = context.device_login['uuid']
    context.get_device_response = context.client.get(
        '/v1/device/{uuid}/setting'.format(uuid=device_id),
        headers=headers
    )
    context.device_etag = context.get_device_response.headers.get('ETag')


@when('try to fetch the device\'s settings using a valid etag')
def get_device_settings_using_etag(context):
    etag = context.device_etag
    access_token = context.device_login['accessToken']
    device_id = context.device_login['uuid']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': etag
    }
    context.get_setting_etag_response = context.client.get(
        '/v1/device/{uuid}/setting'.format(uuid=str(device_id)),
        headers=headers
    )


@then('304 status code should be returned by the device\'s settings endpoint')
def validate_etag_response(context):
    response = context.get_setting_etag_response
    assert_that(response.status_code, equal_to(HTTPStatus.NOT_MODIFIED))


@when('try to fetch the device\'s settings using an expired etag')
def get_device_settings_using_etag(context):
    etag = '123'
    context.device_etag = etag
    access_token = context.device_login['accessToken']
    device_id = context.device_login['uuid']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': etag
    }
    context.get_setting_invalid_etag_response = context.client.get(
        '/v1/device/{uuid}/setting'.format(uuid=str(device_id)),
        headers=headers
    )


@then('200 status code should be returned by the device\'s setting endpoint and a new etag')
def validate_new_etag(context):
    etag = context.device_etag
    response = context.get_setting_invalid_etag_response
    etag_from_response = response.headers.get('ETag')
    assert_that(etag, is_not(etag_from_response))
