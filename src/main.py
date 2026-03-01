"""Main function for Naver Smart Store - Logen Delivery Integration."""

import os
from typing import Optional

from .api_client import NaverCommerceClient
from .transformer import OrderTransformer
from .excel_generator import LogenExcelGenerator
from .utils import generate_logen_filename
from .exceptions import NaverAPIError, DataTransformError, ExcelGenerationError


def generate_logen_shipping_file(access_token: Optional[str] = None) -> str:
    """
    Fetches orders from Naver Smart Store and generates Logen shipping Excel file.
    
    This function orchestrates the entire workflow:
    1. Obtains access token (from parameter or environment variable)
    2. Fetches orders from Naver Commerce API
    3. Transforms order data to Logen format
    4. Generates Excel file with current date in filename
    
    Args:
        access_token: OAuth2 access token for Naver Commerce API.
                     If not provided, reads from NAVER_ACCESS_TOKEN environment variable.
        
    Returns:
        str: Path to generated Excel file
        
    Raises:
        NaverAPIError: When API request fails
        DataTransformError: When data transformation fails
        ExcelGenerationError: When Excel file creation fails
        ValueError: When access token is not provided and not found in environment
    """
    # Read access token from environment variable if not provided as parameter
    if access_token is None:
        access_token = os.environ.get("NAVER_ACCESS_TOKEN")
        if access_token is None:
            raise ValueError(
                "Access token not provided. Please provide access_token parameter "
                "or set NAVER_ACCESS_TOKEN environment variable."
            )
    
    # Instantiate NaverCommerceClient with access_token
    client = NaverCommerceClient(access_token)
    
    # Call fetch_orders to get order data
    orders = client.fetch_orders()
    
    # Call OrderTransformer.transform_to_logen_format to transform data
    transformed_orders = OrderTransformer.transform_to_logen_format(orders)
    
    # Generate output filename using date formatting utility
    filename = generate_logen_filename()
    
    # Call LogenExcelGenerator.generate_excel to create Excel file
    output_path = LogenExcelGenerator.generate_excel(transformed_orders, filename)
    
    # Return path to generated Excel file
    return output_path
