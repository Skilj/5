import random
from csv import DictReader
from datetime import datetime

from pydantic import BaseModel, Field

from test_api.logger import logger


class UserModel(BaseModel):
    username: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)


def __get_users_list_from_csv(path):
    users_list = []

    with open(path, newline='') as f:
        users_data = DictReader(f)

        for user_data in users_data:
            user = UserModel(username=user_data['login'], email=user_data['email'], password=user_data['password'])
            users_list.append(user)

    return users_list


def get_random_user_json(path):
    random_index = random.randint(0, len(__get_users_list_from_csv(path)) - 1)
    random_user_dict = __get_users_list_from_csv(path)[random_index].to_dict()
    user = UserModel.model_validate_json(random_user_dict)

    logger.info("Create random user from csv file:", user=user)

    return user


class StoreModel(BaseModel):
    id: int = Field(default=random.randint(1, 100))
    petId: int = Field(default=random.randint(1, 6))
    quantity: int = Field(default=random.randint(1, 10))
    shipDate: str = Field(default=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
    status: str = Field(default='placed')
    complete: bool = Field(default=random.choice([True, False]))


class ErrorResponse(BaseModel):
    code: int = Field(default=1)
    message: str = Field(default="Order not found")
    type: str = Field(default="error")
