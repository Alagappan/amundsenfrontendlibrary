import json
import responses
import unittest

from http import HTTPStatus

from amundsen_application import create_app
from amundsen_application.api.search.v0 import _create_url_with_field

local_app = create_app('amundsen_application.config.LocalConfig', 'static/templates')


class SearchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_search_results = {
            'total_results': 1,
            'results': [
                {
                    'cluster': 'test_cluster',
                    'column_names': [
                        'column_1',
                        'column_2',
                        'column_3'
                    ],
                    'database': 'test_db',
                    'description': 'This is a test',
                    'key': 'test_key',
                    'last_updated': 1527283287,
                    'name': 'test_table',
                    'schema_name': 'test_schema',
                    'tags': [],
                }
            ]
        }
        self.expected_parsed_search_results = [
            {
                'cluster': 'test_cluster',
                'database': 'test_db',
                'description': 'This is a test',
                'key': 'test_key',
                'last_updated': 1527283287,
                'name': 'test_table',
                'schema_name': 'test_schema',
            }
        ]
        self.bad_search_results = {
            'total_results': 1,
            'results': 'Bad results to trigger exception'
        }

    def test_search_fail_if_no_query(self) -> None:
        """
        Test request failure if 'query' is not provided in the query string
        to the search endpoint
        :return:
        """
        with local_app.test_client() as test:
            response = test.get('/api/search', query_string=dict(page_index='0'))
            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    def test_search_fail_if_no_page_index(self) -> None:
        """
        Test request failure if 'page_index' is not provided in the query string
        to the search endpoint
        :return:
        """
        with local_app.test_client() as test:
            response = test.get('/api/search', query_string=dict(query='test'))
            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    @responses.activate
    def test_search_success(self) -> None:
        """
        Test request success
        :return:
        """
        responses.add(responses.GET, local_app.config['SEARCHSERVICE_ENDPOINT'],
                      json=self.mock_search_results, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/search', query_string=dict(query='test', page_index='0'))
            data = json.loads(response.data)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(data.get('total_results'), self.mock_search_results.get('total_results'))
            self.assertCountEqual(data.get('results'), self.expected_parsed_search_results)

    @responses.activate
    def test_search_fail_on_non_200_response(self) -> None:
        """
        Test request failure if search endpoint returns non-200 http code
        :return:
        """
        responses.add(responses.GET, local_app.config['SEARCHSERVICE_ENDPOINT'],
                      json=self.mock_search_results, status=HTTPStatus.INTERNAL_SERVER_ERROR)

        with local_app.test_client() as test:
            response = test.get('/api/search', query_string=dict(query='test', page_index='0'))
            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    @responses.activate
    def test_search_fail_on_proccessing_bad_response(self) -> None:
        """
        Test catching exception if there is an error processing the results
        from the search endpoint
        :return:
        """
        responses.add(responses.GET, local_app.config['SEARCHSERVICE_ENDPOINT'],
                      json=self.bad_search_results, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/search', query_string=dict(query='test', page_index='0'))
            self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

    @responses.activate
    def test_search_with_field(self) -> None:
        """
        Test search request if user search with colon
        :return:
        """
        responses.add(responses.GET, local_app.config['SEARCHSERVICE_ENDPOINT'],
                      json={}, status=HTTPStatus.OK)

        with local_app.test_client() as test:
            response = test.get('/api/search/field/'
                                'tag_names/field_val/test', query_string=dict(query_term='test',
                                                                              page_index='0'))
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_with_field(self) -> None:
        # test with invalid search term
        with self.assertRaises(Exception):
            invalid_search_term1 = 'tag:hive & schema:default test'
            _create_url_with_field(search_term=invalid_search_term1,
                                   page_index=1)

            invalid_search_term2 = 'tag1:hive tag'
            _create_url_with_field(search_term=invalid_search_term2,
                                   page_index=1)

        with local_app.app_context():
            # test single tag with query term
            search_term = 'tag:hive test_table'
            expected = 'http://0.0.0.0:5001/search/field/tag/field_val' \
                       '/hive?page_index=1&query_term=test_table'
            self.assertEqual(_create_url_with_field(search_term=search_term,
                                                    page_index=1), expected)

            # test single tag without query term
            search_term = 'tag:hive'
            expected = 'http://0.0.0.0:5001/search/field/tag/field_val' \
                       '/hive?page_index=1'
            self.assertEqual(_create_url_with_field(search_term=search_term,
                                                    page_index=1), expected)
