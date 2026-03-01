"""Naver Commerce API client for fetching order data."""

import time
from typing import Dict, List

import requests

from .exceptions import NaverAPIError


class NaverCommerceClient:
    """
    Client for interacting with Naver Commerce API.
    
    This client handles authentication, request retries with exponential backoff,
    and error handling for the Naver Commerce API.
    
    Attributes:
        access_token: OAuth2 access token for API authentication
        base_url: Base URL for Naver Commerce API
        max_retries: Maximum number of retry attempts for failed requests
        initial_delay: Initial delay in seconds for exponential backoff
        backoff_multiplier: Multiplier for exponential backoff delay
    """
    
    def __init__(self, access_token: str):
        """
        Initialize the Naver Commerce API client.
        
        Args:
            access_token: OAuth2 access token for authentication
        """
        self.access_token = access_token
        self.base_url = "https://api.commerce.naver.com/external/v1"
        self.max_retries = 3
        self.initial_delay = 1
        self.backoff_multiplier = 2
    
    def fetch_orders(
        self,
        payment_status: str = "PAYED",
        shipping_status: str = "READY"
    ) -> List[Dict]:
        """
        Fetch orders from Naver Commerce API with specified filters.
        
        This method retrieves orders filtered by payment status and shipping status.
        It implements retry logic with exponential backoff for transient failures
        (5xx errors) and raises NaverAPIError for authentication failures (401)
        and other errors.
        
        Args:
            payment_status: Payment status filter (default: "PAYED")
            shipping_status: Shipping status filter (default: "READY")
        
        Returns:
            List of order dictionaries from the API response
        
        Raises:
            NaverAPIError: When API request fails due to authentication,
                          network errors, or server errors after all retries
        """
        url = f"{self.base_url}/product-orders/query"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "paymentStatus": payment_status,
            "shippingStatus": shipping_status
        }
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                # Handle authentication failure immediately (no retry)
                if response.status_code == 401:
                    raise NaverAPIError(
                        "Authentication failed: Invalid or expired access token",
                        status_code=401,
                        response_body=response.text
                    )
                
                # Handle server errors with retry
                if response.status_code >= 500:
                    last_error = NaverAPIError(
                        f"Server error occurred (attempt {attempt + 1}/{self.max_retries})",
                        status_code=response.status_code,
                        response_body=response.text
                    )
                    
                    # If not the last attempt, wait and retry
                    if attempt < self.max_retries - 1:
                        delay = self.initial_delay * (self.backoff_multiplier ** attempt)
                        time.sleep(delay)
                        continue
                    else:
                        # Last attempt failed, raise the error
                        raise last_error
                
                # Handle other HTTP errors
                if not response.ok:
                    raise NaverAPIError(
                        f"API request failed with status {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text
                    )
                
                # Success - parse and return the response
                data = response.json()
                
                # Extract orders from response
                # The actual API response structure may vary, adjust as needed
                if isinstance(data, dict) and "data" in data:
                    return data.get("data", {}).get("orders", [])
                elif isinstance(data, list):
                    return data
                else:
                    return []
            
            except requests.exceptions.RequestException as e:
                # Network errors - retry with exponential backoff
                last_error = NaverAPIError(
                    f"Network error occurred (attempt {attempt + 1}/{self.max_retries}): {str(e)}",
                    status_code=None,
                    response_body=None
                )
                
                # If not the last attempt, wait and retry
                if attempt < self.max_retries - 1:
                    delay = self.initial_delay * (self.backoff_multiplier ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    # Last attempt failed, raise the error
                    raise last_error
        
        # This should not be reached, but just in case
        if last_error:
            raise last_error
        else:
            raise NaverAPIError("Unknown error occurred during API request")
