#!/usr/bin/env python3
"""Unit tests for GithubOrgClient.
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for the GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct data."""
        expected_result = {"login": org_name}
        mock_get_json.return_value = expected_result

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_result)
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    # @patch("client.GithubOrgClient.org", new_callable=PropertyMock)
    # def test_public_repos_url(self, mock_org):
    #     """Test the _public_repos_url property."""
    #     expected_url = "https://api.github.com/orgs/test_org/repos"
    #     mock_org.return_value = {"repos_url": expected_url}

    #     client = GithubOrgClient("test_org")
    #     self.assertEqual(client._public_repos_url, expected_url)

    # @patch("client.GithubOrgClient.repos_payload", new_callable=PropertyMock)
    # def test_public_repos(self, mock_repos_payload):
        """Test the public_repos method."""
    #     mock_repos_payload.return_value = [
    #         {"name": "repo1"},
    #         {"name": "repo2"}
    #     ]
            
    #     client = GithubOrgClient("test_org")
    #     self.assertEqual(client.public_repos(), ["repo1", "repo2"])
    #     mock_repos_payload.assert_called_once()

    # @parameterized.expand([
    #     ("repo_with_license", {"license": {"key": "my_license"}}, "my_license", True),
    #     ("repo_with_other_license", {"license": {"key": "other_license"}}, "my_license", False),
    # ])
    # def test_has_license(self, name, repo, license_key, expected):
        """Test has_license static method."""
    #     result = GithubOrgClient.has_license(repo, license_key)
    #     self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD["org_payload"],
        "repos_payload": TEST_PAYLOAD["repos_payload"],
        "expected_repos": TEST_PAYLOAD["expected_repos"],
        "apache2_repos": TEST_PAYLOAD["apache2_repos"],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Start patcher for requests.get."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        cls.mock_get.side_effect = [
            unittest.mock.Mock(**{"json.return_value": cls.org_payload}),
            unittest.mock.Mock(**{"json.return_value": cls.repos_payload})
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repo names."""
        client = GithubOrgClient("test_org")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos filters by license."""
        client = GithubOrgClient("test_org")
        self.assertEqual(client.public_repos(license="apache-2.0"), self.apache2_repos)

