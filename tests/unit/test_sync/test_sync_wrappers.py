"""Basic tests for synchronous wrappers."""

from unittest.mock import AsyncMock, MagicMock, patch

from pysophoscentralapi.sync.client import HTTPClientSync
from pysophoscentralapi.sync.utils import run_async


class TestSyncUtils:
    """Tests for sync utility functions."""

    def test_run_async(self):
        """Test run_async executes coroutine synchronously."""

        async def sample_coro():
            return "test_result"

        result = run_async(sample_coro())
        assert result == "test_result"


class TestHTTPClientSync:
    """Tests for HTTPClientSync."""

    @patch("pysophoscentralapi.sync.client.HTTPClient")
    def test_context_manager(self, mock_http_client_class):
        """Test HTTPClientSync context manager."""
        mock_auth = MagicMock()
        mock_async_client = AsyncMock()
        mock_http_client_class.return_value = mock_async_client

        with patch("pysophoscentralapi.sync.client.run_async") as mock_run_async:
            # Mock __aenter__ and __aexit__
            mock_async_client.__aenter__.return_value = mock_async_client
            mock_async_client.__aexit__.return_value = None

            with HTTPClientSync("https://api.example.com", mock_auth) as client:
                assert client is not None
                assert isinstance(client, HTTPClientSync)

            # Verify __aenter__ and __aexit__ were called
            assert mock_run_async.call_count == 2  # enter and exit

    @patch("pysophoscentralapi.sync.client.HTTPClient")
    def test_get_method(self, mock_http_client_class):
        """Test synchronous GET method."""
        mock_auth = MagicMock()
        mock_async_client = AsyncMock()
        mock_http_client_class.return_value = mock_async_client

        mock_async_client.get.return_value = {"data": "value"}

        with patch("pysophoscentralapi.sync.client.run_async") as mock_run_async:
            # Mock __aenter__ to return the client
            mock_run_async.side_effect = [
                mock_async_client,  # __aenter__
                {"data": "value"},  # get
                None,  # __aexit__
            ]

            with HTTPClientSync("https://api.example.com", mock_auth) as client:
                result = client.get("/test", {"param": "value"})

            assert result == {"data": "value"}
