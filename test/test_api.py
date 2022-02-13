import json
from pathlib import Path

import pytest
import requests

from intrusion_monitor.api import process_request, url_builder

test_data = Path(__file__).parent.joinpath("test_data")


class TestProcessRequestClass:
    def test_api_code_200_valid(self, requests_mock):
        file = test_data / "api_response" / "ip-api_200_valid.json"
        json_data = self.get_json_from_file(file)

        req_mock = self.get_mocked_request(json_data, requests_mock)

        assert json_data == process_request(req_mock)

    def test_api_code_200_invalid(self, requests_mock):
        file = test_data / "api_response" / "ip-api_200_valid.json"
        json_data = self.get_json_from_file(file)

        req_mock = self.get_mocked_request(json_data, requests_mock)

        assert json_data == process_request(req_mock)

    def test_api_code_200_private(self, requests_mock):
        file = test_data / "api_response" / "ip-api_200_valid.json"
        json_data = self.get_json_from_file(file)

        req_mock = self.get_mocked_request(json_data, requests_mock)

        assert json_data == process_request(req_mock)

    def test_api_code_200_reserved(self, requests_mock):
        file = test_data / "api_response" / "ip-api_200_valid.json"
        json_data = self.get_json_from_file(file)

        req_mock = self.get_mocked_request(json_data, requests_mock)

        assert json_data == process_request(req_mock)

    def test_api_code_non_200(self, requests_mock):
        file = test_data / "api_response" / "ip-api_403.json"
        json_data = self.get_json_from_file(file)

        req_mock = self.get_mocked_request(json_data, requests_mock, status_code=403)

        with pytest.raises(requests.HTTPError):
            process_request(req_mock)

    @staticmethod
    def get_mocked_request(json_data, requests_mock, status_code=200):
        requests_mock.get("http://test.com", json=json_data, status_code=status_code)
        req_mock = requests.get("http://test.com")

        # Set from_cache to false, since we use requests-cache and not requests
        req_mock.from_cache = False
        return req_mock

    @staticmethod
    def get_json_from_file(file):
        with open(file, "r") as f:
            json_data = json.load(f)
        return json_data


class TestIpApiHealthClass:
    def test_api_connection(self):
        url_str = url_builder(ip=None, base_url=True)

        req = requests.get(url_str)
        req_json = req.json()

        assert req.status_code == 200 and req_json["status"] == "success"

    def test_api_returns_expected(self):
        url_str = url_builder(ip="1.1.1.1", fields_id=66846719)

        req_json = requests.get(url_str).json()

        file = test_data / "api_response" / "ip-api_query_1-1-1-1_66846719.json"
        expected_json = TestProcessRequestClass.get_json_from_file(file)

        assert req_json == expected_json
