import requests

BASE_URL = "https://api.notion.com/v1"
PAGE_PATH = "pages"
DATABASE_PATH = "databases"
NOTION_VERSION_STRING = "2021-08-16"


class UnableToCompleteRequestException(Exception):
    pass


class Client:
    def __init__(self, api_key):
        self.headers = {
            "Notion-Version": NOTION_VERSION_STRING,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def __get(self, path):
        url = f"{BASE_URL}/{path}"
        return requests.get(url, headers=self.headers)

    def __post(self, path, data):
        url = f"{BASE_URL}/{path}"
        return requests.post(url, data=data, headers=self.headers)

    def __patch(self, path, data):
        url = f"{BASE_URL}/{path}"
        return requests.patch(url, data=data, headers=self.headers)

    def get_database(self, database_id):
        path = f"{DATABASE_PATH}/{database_id}"
        response = self.__get(path)
        if response.status_code != 200:
            raise UnableToCompleteRequestException(response.text)
        return response.text

    def get_database_contents(self, database_id):
        path = f"{DATABASE_PATH}/{database_id}/query"
        response = self.__post(path, data=None)
        if response.status_code != 200:
            raise UnableToCompleteRequestException(response.text)
        return response.text

    def create_page(self, data):
        path = f"{PAGE_PATH}"
        response = self.__post(path, data)
        if response.status_code != 200:
            raise UnableToCompleteRequestException(response.text)
        return response.text

    def update_page_content(self, page_id, data):
        path = f"{PAGE_PATH}/{page_id}"
        response = self.__patch(path, data)
        if response.status_code != 200:
            raise UnableToCompleteRequestException(response.text)
        return response.text

    def get_page(self, page_id):
        path = f"{PAGE_PATH}/{page_id}"
        response = self.__get(path)
        if response.status_code != 200:
            raise UnableToCompleteRequestException(response.text)
        return response.text
