#!/usr/bin/env python3
"""Unit and integration tests for client.GithubOrgClient

This module contains test cases to verify the functionality of the GithubOrgClient
class, including its properties and methods, using both unit tests with mocking
and integration tests with fixtures.
"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from typing import Dict, List
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos

class TestGithubOrgClient(unittest.TestCase):
    """Test case class for GithubOrgClient

    This class contains unit tests to validate the behavior of GithubOrgClient's
    properties and methods under controlled conditions using mocks.
    """

    @parameterized.expand([
        ("google", {"name": "google", "repos_url": "https://api.github.com/orgs/google/repos"}),
        ("abc", {"name": "abc", "repos_url": "https://api.github.com/orgs/abc/repos"})
    ])
    @patch('utils.get_json')
    def test_org(self, org_name: str, expected_payload: Dict, mock_get_json: Mock) -> None:
        """Test that GithubOrgClient.org returns the correct value

        Args:
            org_name: The name of the organization to test
            expected_payload: The expected dictionary returned by org
            mock_get_json: Mock object for get_json function
        """
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    def test_public_repos_url(self) -> None:
        """Test that GithubOrgClient._public_repos_url returns the expected URL

        This test mocks the org property to return a known payload and verifies
        that _public_repos_url extracts the correct repos_url.
        """
        with patch.object(GithubOrgClient, 'org', new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": "https://api.github.com/orgs/test_org/repos"}
            client = GithubOrgClient("test_org")
            self.assertEqual(client._public_repos_url, "https://api.github.com/orgs/test_org/repos")

    @patch('utils.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Test that GithubOrgClient.public_repos returns the expected list of repos

        This test mocks _public_repos_url and get_json to control the data flow
        and verifies the returned repository names and call counts.

        Args:
            mock_get_json: Mock object for get_json function
        """
        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = "https://api.github.com/orgs/test_org/repos"
            mock_get_json.return_value = [
                {"name": "repo1", "license": {"key": "mit"}},
                {"name": "repo2", "license": {"key": "apache-2.0"}}
            ]
            client = GithubOrgClient("test_org")
            repos = client.public_repos()
            self.assertEqual(repos, ["repo1", "repo2"])
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/test_org/repos")
            mock_public_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo: Dict, license_key: str, expected: bool) -> None:
        """Test that GithubOrgClient.has_license returns the correct boolean

        Args:
            repo: Dictionary representing a repository
            license_key: The license key to check against
            expected: The expected boolean result
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

@parameterized_class([
    {
        "org_name": "test_org",
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test case class for GithubOrgClient

    This class tests GithubOrgClient.public_repos in an integration scenario,
    mocking external HTTP requests with fixtures to simulate real responses.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class method to start mocking requests.get

        This method initializes a patcher for requests.get and configures it
        to return mocked responses based on the URL using fixtures.
        """
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.side_effect = cls.get_response

    @classmethod
    def get_response(cls, url: str) -> Mock:
        """Return a mocked response based on the requested URL

        Args:
            url: The URL being requested

        Returns:
            A Mock object with a json method returning the appropriate fixture
        """
        if url == GithubOrgClient.ORG_URL.format(org=cls.org_name):
            return Mock(json=Mock(return_value=cls.org_payload))
        elif url == cls.org_payload["repos_url"]:
            return Mock(json=Mock(return_value=cls.repos_payload))
        else:
            raise ValueError(f"Unexpected URL: {url}")

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down class method to stop the patcher

        This method stops the patcher started in setUpClass to clean up.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test that public_repos returns the expected list of repositories"""
        client = GithubOrgClient(self.org_name)
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Test that public_repos with license filter returns the expected list"""
        client = GithubOrgClient(self.org_name)
        self.assertEqual(client.public_repos(license="apache-2.0"), self.apache2_repos)

if __name__ == "__main__":
    unittest.main()
