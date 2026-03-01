"""Unit tests for NaverCommerceClient."""

import pytest
from unittest.mock import Mock, patch
import requests
import sys
import os
import importlib.util

# Import modules directly without triggering src/__init__.py
def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Import exceptions first
exceptions_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'exceptions.py')
exceptions = import_module_from_path('src.exceptions', exceptions_path)
NaverAPIError = exceptions.NaverAPIError

# Import api_client
api_client_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'api_client.py')
api_client = import_module_from_path('src.api_client', api_client_path)
NaverCommerceClient = api_client.NaverCommerceClient


class TestNaverCommerceClient:
    """Test suite for NaverCommerceClient class."""
    
    def test_init_stores_access_token(self):
        """Test that __init__ correctly stores the access token."""
        token = "test_access_token_12345"
        client = NaverCommerceClient(token)
        
        assert client.access_token == token
        assert client.max_retries == 3
        assert client.initial_delay == 1
        assert client.backoff_multiplier == 2
    
    @patch('requests.get')
    def test_fetch_orders_success(self, mock_get):
        """Test successful order fetching with default parameters."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "orders": [
                    {"orderId": "1", "productName": "Product 1"},
                    {"orderId": "2", "productName": "Product 2"}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        client = NaverCommerceClient("test_token")
        orders = client.fetch_orders()
        
        assert len(orders) == 2
        assert orders[0]["orderId"] == "1"
        assert orders[1]["productName"] == "Product 2"
        
        # Verify correct API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "Bearer test_token" in call_args.kwargs["headers"]["Authorization"]
        assert call_args.kwargs["params"]["paymentStatus"] == "PAYED"
        assert call_args.kwargs["params"]["shippingStatus"] == "READY"
    
    @patch('requests.get')
    def test_fetch_orders_with_custom_status(self, mock_get):
        """Test order fetching with custom payment and shipping status."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"orders": []}}
        mock_get.return_value = mock_response
        
        client = NaverCommerceClient("test_token")
        client.fetch_orders(payment_status="CANCELED", shipping_status="DISPATCHED")
        
        call_args = mock_get.call_args
        assert call_args.kwargs["params"]["paymentStatus"] == "CANCELED"
        assert call_args.kwargs["params"]["shippingStatus"] == "DISPATCHED"
    
    @patch('requests.get')
    def test_fetch_orders_401_raises_naver_api_error(self, mock_get):
        """Test that 401 status code raises NaverAPIError immediately."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        client = NaverCommerceClient("invalid_token")
        
        with pytest.raises(NaverAPIError) as exc_info:
            client.fetch_orders()
        
        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)
        # Should not retry on 401
        assert mock_get.call_count == 1
    
    @patch('time.sleep')
    @patch('requests.get')
    def test_fetch_orders_5xx_retries_with_exponential_backoff(self, mock_get, mock_sleep):
        """Test that 5xx errors trigger retry with exponential backoff."""
        # Mock 500 error for all attempts
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        client = NaverCommerceClient("test_token")
        
        with pytest.raises(NaverAPIError) as exc_info:
            client.fetch_orders()
        
        # Should retry 3 times
        assert mock_get.call_count == 3
        assert exc_info.value.status_code == 500
        
        # Verify exponential backoff: 1s, 2s (no sleep after last attempt)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # First retry: 1 * 2^0 = 1
        mock_sleep.assert_any_call(2)  # Second retry: 1 * 2^1 = 2
    
    @patch('time.sleep')
    @patch('requests.get')
    def test_fetch_orders_5xx_success_after_retry(self, mock_get, mock_sleep):
        """Test successful request after initial 5xx error."""
        # First call fails with 500, second call succeeds
        mock_error_response = Mock()
        mock_error_response.ok = False
        mock_error_response.status_code = 500
        mock_error_response.text = "Internal Server Error"
        
        mock_success_response = Mock()
        mock_success_response.ok = True
        mock_success_response.status_code = 200
        mock_success_response.json.return_value = {
            "data": {"orders": [{"orderId": "123"}]}
        }
        
        mock_get.side_effect = [mock_error_response, mock_success_response]
        
        client = NaverCommerceClient("test_token")
        orders = client.fetch_orders()
        
        assert len(orders) == 1
        assert orders[0]["orderId"] == "123"
        assert mock_get.call_count == 2
        assert mock_sleep.call_count == 1  # Slept once before retry
    
    @patch('requests.get')
    def test_fetch_orders_network_error_retries(self, mock_get):
        """Test that network errors trigger retry logic."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        client = NaverCommerceClient("test_token")
        
        with pytest.raises(NaverAPIError) as exc_info:
            client.fetch_orders()
        
        assert mock_get.call_count == 3
        assert "Network error" in str(exc_info.value)
    
    @patch('requests.get')
    def test_fetch_orders_other_http_error(self, mock_get):
        """Test handling of other HTTP errors (not 401 or 5xx)."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response
        
        client = NaverCommerceClient("test_token")
        
        with pytest.raises(NaverAPIError) as exc_info:
            client.fetch_orders()
        
        assert exc_info.value.status_code == 400
        assert "API request failed" in str(exc_info.value)
    
    @patch('requests.get')
    def test_fetch_orders_empty_response(self, mock_get):
        """Test handling of empty order list response."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"orders": []}}
        mock_get.return_value = mock_response
        
        client = NaverCommerceClient("test_token")
        orders = client.fetch_orders()
        
        assert orders == []
    
    @patch('requests.get')
    def test_fetch_orders_list_response_format(self, mock_get):
        """Test handling of response that is directly a list."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"orderId": "1"},
            {"orderId": "2"}
        ]
        mock_get.return_value = mock_response
        
        client = NaverCommerceClient("test_token")
        orders = client.fetch_orders()
        
        assert len(orders) == 2
        assert orders[0]["orderId"] == "1"
