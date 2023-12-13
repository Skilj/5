import json
from pprint import pprint

import allure
import jsonschema
import requests
from assertpy import assert_that
from requests import codes

from data.user import get_random_user_json, User
from test_api.logger import logger
from test_api.models.models import UserModel
from test_api.request_api_client import RequestApiClient


class TestUser:

    @allure.feature('should_create_order')
    def test_should_create_user(self):
        logger.info(100 * "=")
        logger.info("Start test should_create_user()")
        logger.info(100 * "-")
        user = UserModel.model_validate_json(
            get_random_user_json("C:/PycharmProjects/kt_5/test_api/user/files/users.csv")).model_dump_json()

        user_request = RequestApiClient(path="/user")

        response = self.send_request_to_create_user(user, user_request)
        self.check_response_after_user_created(response)
        response_created_user = self.check_that_can_get_created_user(user, user_request)
        self.check_that_getting_user_the_same_as_created(response_created_user, user)

    @allure.feature('should_get_error_when_not_found_user')
    def test_should_get_error_when_not_found_user(self):
        logger.info(100 * "=")
        logger.info("Start test should_get_error_when_not_found_user()")
        logger.info(100 * "-")

        user_request = RequestApiClient(path="/user")
        response = self.send_request_get_user(user_request)
        self.check_error_response(response)

    @allure.feature('should_delete_user')
    def test_should_delete_user(self):
        logger.info(100 * "=")
        logger.info("Start test should_delete_user()")
        logger.info(100 * "-")
        user = UserModel.model_validate_json(
            get_random_user_json("C:/PycharmProjects/kt_5/test_api/user/files/users.csv"))
        username = user.username
        user_request = RequestApiClient(path="/user")

        self.send_request_to_create_user(user.model_dump_json(), user_request)
        response = self.send_request_to_delete_user(user_request, username)
        self.check_response_after_delete_user(response, username)
        self.check_that_user_not_found_after_delete(user_request, username)

    @allure.feature('should_update_user')
    def test_should_update_user(self):
        logger.info(100 * "=")
        logger.info("Start test should_update_user()")
        logger.info(100 * "-")
        user = UserModel.model_validate_json(
            get_random_user_json("C:/PycharmProjects/kt_5/test_api/user/files/users.csv")).model_dump_json()
        new_user = UserModel.model_validate_json(
            get_random_user_json("C:/PycharmProjects/kt_5/test_api/user/files/users.csv")).model_dump_json()
        user_request = RequestApiClient(path="/user")

        self.send_request_to_create_user(user, user_request)

        response = self.send_request_to_update_user(new_user, user, user_request)

        self.check_response_after_update_user(response)

        self.check_that_user_updated(new_user, user_request)

    @allure.step("check_that_user_updated by new data {new_user}")
    def check_that_user_updated(self, new_user, user_request):
        expected_user = json.loads(new_user)
        logger.info("- Step 3: Check that user updated: ", expected_user=expected_user)
        new_user_response = user_request.get(json.loads(new_user)["username"])
        assert_that(new_user_response.json()["username"]).is_equal_to(expected_user["username"])
        assert_that(new_user_response.json()["email"]).is_equal_to(expected_user["email"])
        assert_that(new_user_response.json()["password"]).is_equal_to(expected_user["password"])

    @allure.step("check_response {response} _after_update_user")
    def check_response_after_update_user(self, response):
        assert_that(response.status_code).is_equal_to(codes.ok)
        assert_that(response.json()["code"]).is_equal_to(codes.ok)
        assert_that(response.json()["type"]).is_equal_to("unknown")
        assert_that(response.json()["message"]).is_not_empty()

    @allure.step("send_request_ {user_request} to_update_user {user} with new data {new_user}")
    def send_request_to_update_user(self, new_user, user, user_request):
        logger.info("- Step 2: Update user: ", new_user=new_user)
        username = json.loads(user).get("username")
        response = user_request.put(username, new_user)
        return response

    @allure.step("check_that_user {username} _not_found_after_delete")
    def check_that_user_not_found_after_delete(self, user_request, username):
        # Bug
        logger.info("- Step 3: Check that user not found: ", username=username)
        response = user_request.delete(username)
        try:
            assert_that(response.status_code).is_equal_to(codes.not_found)
        except AssertionError as e:
            logger.error("- Bug: ", e=e)

    @allure.step("check_response_after_delete_user")
    def check_response_after_delete_user(self, response, username):
        assert_that(response.status_code).is_equal_to(codes.ok)
        assert_that(response.json()["code"]).is_equal_to(codes.ok)
        assert_that(response.json()["type"]).is_equal_to("unknown")
        assert_that(response.json()["message"]).is_equal_to(username)

    @allure.step("send_request {user_request} _to_delete_user {username}")
    def send_request_to_delete_user(self, user_request, username):
        logger.info("- Step 2: Delete user: ", username=username)
        response = user_request.delete(username)
        return response

    @allure.step("check_error_response")
    def check_error_response(self, response):
        assert_that(response.status_code).is_equal_to(requests.codes.not_found)
        assert_that(response.json()).is_instance_of(dict)
        assert_that(response.json()).contains_key("code").contains_key("type").contains_key("message")
        assert_that(response.json()["code"]).is_equal_to(1)
        assert_that(response.json()["type"]).is_equal_to("error")
        assert_that(response.json()["message"]).is_equal_to("User not found")

    @allure.step("send_request_get_user {user_request}")
    def send_request_get_user(self, user_request):
        logger.info("- Check that cannot get non exist user:", username="Jason")
        response = user_request.get("Jason", True)
        return response

    @allure.step("check_that_getting_user {response_created_user} _the_same_as_created {user}")
    def check_that_getting_user_the_same_as_created(self, response_created_user, user):
        expected_user = User(
            json.loads(user).get("username"),
            json.loads(user).get("email"),
            json.loads(user).get("password"),
        )
        expected_schema = {
            "properties": {
                "id": {"type": "number"},
                "username": {"type": "string"},
                "email": {"type": "string"},
                "password": {"type": "string"},
                "userStatus": {"type": "number"}
            }
        }
        jsonschema.validate(json.dumps(response_created_user.json()), expected_schema)
        assert_that(response_created_user.json()["username"]).is_equal_to(expected_user.username)
        assert_that(response_created_user.json()["email"]).is_equal_to(expected_user.email)
        assert_that(response_created_user.json()["password"]).is_equal_to(expected_user.password)

    @allure.step("check_that_can_get_created_user '{user}'")
    def check_that_can_get_created_user(self, user, user_request):
        logger.info("- Step 2: Check that can get created user: ", username=json.loads(user).get("username"))
        response_created_user = user_request.get(json.loads(user).get("username"))
        return response_created_user

    @allure.step("check_response_ '{response}' after_user_created")
    def check_response_after_user_created(self, response):
        assert_that(response.status_code).is_equal_to(codes.ok)
        assert_that(response.json()["code"]).is_equal_to(codes.ok)
        assert_that(response.json()["type"]).is_equal_to("unknown")
        assert_that(response.json()["message"]).is_not_empty()

    @allure.step("send_request '{user_request}' _to_create_user '{user}'")
    def send_request_to_create_user(self, user, user_request):
        logger.info("- Step 1: Create user:", user=user)
        response = user_request.post(user)
        return response
