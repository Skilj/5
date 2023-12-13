import allure
from assertpy import assert_that
from requests import codes

from test_api.logger import logger
from test_api.models.models import UserModel, get_random_user_json, StoreModel, ErrorResponse
from test_api.request_api_client import RequestApiClient
from test_api.store.data.store import get_random_store, Store


class TestStore:

    @allure.feature('should_create_order')
    def test_create_order(self):
        logger.info(100 * "=")
        logger.info("Start test should_create_order()")
        logger.info(100 * "-")
        store = StoreModel().__dict__
        store_request = RequestApiClient(path="/store/order")

        response = self.send_post_request_and_get_response(store, store_request)
        self.check_response(response, store)

    @allure.feature('should_get_error_when_not_found_order')
    def test_get_error_when_not_found_order(self):
        logger.info(100 * "=")
        logger.info("Start test should_get_error_when_not_found_order()")
        logger.info(100 * "-")
        store_request = RequestApiClient(path="/store/order")
        response = self.send_get_request_with_path_variable_and_get_response(11, store_request)
        self.check_error_response(response)

    @allure.feature("should_get_order")
    def test_get_order(self):
        logger.info(100 * "=")
        logger.info("Start test should_get_order()")
        logger.info(100 * "-")

        store_request = RequestApiClient(path="/store/order")
        store = StoreModel().__dict__

        response = self.create_order(store, store_request)
        self.check_order_is_created(response)

        order_id = store.get("id")
        response = self.send_get_request_to_get_order(order_id, store_request)
        self.check_that_getting_order_is_equals_created(order_id, response, store)

    @allure.feature("should_delete_order")
    def test_delete_order(self):
        logger.info(100 * "=")
        logger.info("Start test should_delete_order()")
        logger.info(100 * "-")
        store = StoreModel().__dict__
        store_request = RequestApiClient(path="/store/order")

        self.create_order(store, store_request)

        response, store_id = self.send_request_to_delete_order(store, store_request)
        self.check_response_after_delete(response, store_id)

    @allure.step("check_response '{response}' _after_delete '{store_id}'")
    def check_response_after_delete(self, response, store_id):
        assert_that(response.status_code).is_equal_to(codes.ok)
        assert_that(response.json()["code"]).is_equal_to(codes.ok)
        assert_that(response.json()["type"]).is_equal_to("unknown")
        assert_that(response.json()["message"]).is_equal_to(store_id.__str__())

    @allure.step("send_request '{store_request}' _to_delete_order '{store}'")
    def send_request_to_delete_order(self, store, store_request):
        logger.info("- Step 2: Delete order: ", store=store)
        store_id = store.get("id")
        response = store_request.delete(store_id)
        return response, store_id

    @allure.step("check_that response '{response}' getting order by '{order_id}'is equals created '{store}'")
    def check_that_getting_order_is_equals_created(self, order_id, response, store):
        expected_order_id = Store(order_id, store.get("petId"), store.get("quantity"), store.get("shipDate"),
                                  store.get("status"), store.get("complete"))
        assert_that(response.status_code).is_equal_to(codes.ok)
        assert_that(response.json()["id"]).is_equal_to(expected_order_id.__getattribute__("id"))
        assert_that(response.json()["petId"]).is_equal_to(expected_order_id.__getattribute__("petId"))
        assert_that(response.json()["quantity"]).is_equal_to(expected_order_id.__getattribute__("quantity"))
        assert_that(response.json()["shipDate"]).contains(expected_order_id.__getattribute__("shipDate"))
        assert_that(response.json()["status"]).is_equal_to(expected_order_id.__getattribute__("status"))
        assert_that(response.json()["complete"]).is_equal_to(expected_order_id.__getattribute__("complete"))

    @allure.step("send_get_request_ '{store_request}' _to_get_order")
    def send_get_request_to_get_order(self, order_id, store_request):
        logger.info("- Check can get order:", order_id=order_id)
        return store_request.get(order_id)

    @allure.step("check_order_is_created")
    def check_order_is_created(self, response):
        assert_that(response.status_code).is_equal_to(codes.ok)

    @allure.step("Create order with '{store}', sending '{store_request}'")
    def create_order(self, store, store_request):
        logger.info("- Step 1: Create order:", store=store)
        return store_request.post(store)

    @allure.step("Check '{response}' equals data '{store}'")
    def check_response(self, response, store):
        assert_that(response.status_code).is_equal_to(codes.ok)
        try:
            assert_that(response.json()).is_equal_to(store)
        except AssertionError as e:
            logger.error("- Bug (wrong milliseconds):", e=e)

    @allure.step("Send POST request '{store_request}' with data '{store}'")
    def send_post_request_and_get_response(self, store, store_request):
        logger.info("- Step 1: Create order:", store=store)
        response = store_request.post(store)
        return response

    @allure.step("Send GET request with path variable '{store_request}'")
    def send_get_request_with_path_variable_and_get_response(self, pet_id, store_request):
        logger.info("- Check error when pet ID > 10:", pet_id=pet_id)
        response = store_request.get(pet_id, True)
        return response

    @allure.step("Check error response '{response}'")
    def check_error_response(self, response):
        ErrorResponse().model_validate_json(response)
        assert_that(response.status_code).is_equal_to(codes.not_found)
        assert_that(response.json()["code"]).is_equal_to(1)
        assert_that(response.json()["type"]).is_equal_to("error")
        assert_that(response.json()["message"]).is_equal_to("Order not found")
