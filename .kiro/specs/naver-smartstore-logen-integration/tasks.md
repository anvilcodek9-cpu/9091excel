# Implementation Plan: Naver Smart Store - Logen Delivery Integration

## Overview

This implementation plan breaks down the Naver Smart Store and Logen delivery integration system into discrete coding tasks. The system will be implemented in Python with three main components: API client, data transformer, and Excel generator. All property-based tests will use hypothesis and pytest, with test files organized in a tests/ folder.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: src/ for main code, tests/ for test files
  - Create requirements.txt with dependencies: requests, openpyxl, pytest, hypothesis
  - Create __init__.py files for Python package structure
  - Define custom exception classes: NaverAPIError, DataTransformError, ExcelGenerationError
  - _Requirements: 1.3, 1.5, 3.1-3.5, 4.9_

- [x] 2. Implement data models
  - [x] 2.1 Create NaverOrder and LogenShipment dataclasses
    - Define NaverOrder dataclass with all required fields (order_id, product_order_id, receiver_name, base_address, detailed_address, receiver_tel1, product_name, delivery_memo, payment_status, shipping_status)
    - Define LogenShipment dataclass with Logen format fields (receiver_name, full_address, receiver_tel, product_name, delivery_memo)
    - _Requirements: 2.1-2.6, 3.1-3.5_

- [-] 3. Implement OrderTransformer component
  - [x] 3.1 Create OrderTransformer class with transform_to_logen_format method
    - Implement field validation for required fields (receiverName, baseAddress, detailedAddress, receiverTel1, productName)
    - Implement direct field mapping for receiverName → receiver_name, receiverTel1 → receiver_tel, productName → product_name
    - Implement address concatenation: baseAddress + " " + detailedAddress → full_address (pay special attention to space handling)
    - Handle null deliveryMemo by using empty string
    - Raise DataTransformError with order ID and field name when required fields are missing
    - _Requirements: 2.1-2.6, 3.1-3.5_
  
  - [ ]* 3.2 Write property test for direct field mapping preservation
    - **Property 2: Direct Field Mapping Preservation**
    - **Validates: Requirements 2.1, 2.4, 2.5**
    - Generate random Naver orders with various receiverName, receiverTel1, productName values
    - Verify transformed data contains identical values for these fields
    - Tag: `Feature: naver-smartstore-logen-integration, Property 2: Direct Field Mapping Preservation`
  
  - [ ]* 3.3 Write property test for address concatenation
    - **Property 3: Address Concatenation**
    - **Validates: Requirements 2.2**
    - Generate random baseAddress and detailedAddress strings
    - Verify full_address equals baseAddress + " " + detailedAddress
    - Tag: `Feature: naver-smartstore-logen-integration, Property 3: Address Concatenation`
  
  - [ ]* 3.4 Write property test for data validation error handling
    - **Property 7: Data Validation Error Handling**
    - **Validates: Requirements 3.1-3.5**
    - Generate random orders with one or more required fields missing
    - Verify DataTransformError is raised with order ID and field name
    - Tag: `Feature: naver-smartstore-logen-integration, Property 7: Data Validation Error Handling`
  
  - [ ]* 3.5 Write unit tests for OrderTransformer edge cases
    - Test missing deliveryMemo field (should use empty string)
    - Test empty string in optional fields
    - Test address concatenation with various whitespace scenarios
    - _Requirements: 2.6_

- [ ] 4. Implement NaverCommerceClient component
  - [x] 4.1 Create NaverCommerceClient class with fetch_orders method
    - Implement __init__ method to accept and store access_token
    - Implement fetch_orders method with payment_status and shipping_status parameters (defaults: "PAYED", "READY")
    - Build HTTP request to Naver Commerce API with proper authentication headers
    - Implement retry logic with exponential backoff (max 3 attempts, initial delay 1s, multiplier 2x)
    - Handle HTTP error responses: raise NaverAPIError for 401, 5xx errors
    - Parse JSON response and return list of order dictionaries
    - _Requirements: 1.1-1.6_
  
  - [ ]* 4.2 Write property test for API status filtering
    - **Property 1: API Status Filtering**
    - **Validates: Requirements 1.1, 1.2**
    - Generate random valid access tokens
    - Mock API client and verify correct status filter parameters are sent
    - Tag: `Feature: naver-smartstore-logen-integration, Property 1: API Status Filtering`
  
  - [ ]* 4.3 Write property test for API error propagation
    - **Property 6: API Error Propagation**
    - **Validates: Requirements 1.3, 1.5**
    - Generate random HTTP error responses (401, 5xx)
    - Verify NaverAPIError is raised with appropriate message
    - Tag: `Feature: naver-smartstore-logen-integration, Property 6: API Error Propagation`
  
  - [ ]* 4.4 Write unit tests for API client
    - Test successful API response parsing
    - Test 401 authentication failure
    - Test network timeout and retry logic
    - Test retry exhaustion after 3 attempts
    - _Requirements: 1.3-1.5_

- [x] 5. Checkpoint - Ensure core components work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement LogenExcelGenerator component
  - [x] 6.1 Create LogenExcelGenerator class with generate_excel method
    - Implement generate_excel static method accepting data list and output_path
    - Create Excel workbook using openpyxl
    - Create header row with columns: "받는사람", "주소", "전화번호", "상품명", "배송메모"
    - Iterate through data and create rows starting from row 2
    - Place fields in correct columns: receiver_name (A), full_address (B), receiver_tel (C), product_name (D), delivery_memo (E)
    - Save workbook to output_path
    - Handle file system errors and raise ExcelGenerationError with path and error details
    - Return path to generated file
    - _Requirements: 4.1-4.9_
  
  - [ ]* 6.2 Write property test for Excel row structure
    - **Property 5: Excel Row Structure**
    - **Validates: Requirements 4.3**
    - Generate random lists of transformed orders (0 to 100 orders)
    - Verify Excel has header row + N data rows where N = order count
    - Tag: `Feature: naver-smartstore-logen-integration, Property 5: Excel Row Structure`
  
  - [ ]* 6.3 Write unit tests for Excel generator
    - Test Excel header row contains correct columns in correct order
    - Test empty orders list produces only header row
    - Test data placement in correct columns
    - Test file system error handling
    - _Requirements: 4.2, 4.4-4.8_

- [x] 7. Implement filename generation with date formatting
  - [x] 7.1 Create utility function for generating dated filename
    - Implement function to generate filename in format "로젠발송양식_{YYYYMMDD}.xlsx"
    - Use datetime.now() to get current date
    - Format date as YYYYMMDD string
    - _Requirements: 4.1_
  
  - [ ]* 7.2 Write property test for filename date format
    - **Property 4: Filename Date Format**
    - **Validates: Requirements 4.1**
    - Generate random dates
    - Verify filename matches pattern with correct date
    - Tag: `Feature: naver-smartstore-logen-integration, Property 4: Filename Date Format`
  
  - [ ]* 7.3 Write unit tests for filename generation
    - Test filename format with known dates
    - Test filename includes Korean characters correctly
    - _Requirements: 4.1_

- [x] 8. Implement main function integration
  - [x] 8.1 Create generate_logen_shipping_file main function
    - Implement function signature accepting access_token parameter
    - Add logic to read access_token from environment variable if not provided as parameter
    - Instantiate NaverCommerceClient with access_token
    - Call fetch_orders to get order data
    - Call OrderTransformer.transform_to_logen_format to transform data
    - Generate output filename using date formatting utility
    - Call LogenExcelGenerator.generate_excel to create Excel file
    - Return path to generated Excel file
    - Propagate all exceptions (NaverAPIError, DataTransformError, ExcelGenerationError) to caller
    - _Requirements: 6.1-6.5_
  
  - [ ]* 8.2 Write integration tests for main function
    - Test end-to-end success path with mocked API
    - Test error propagation from each component
    - Test environment variable fallback for access_token
    - _Requirements: 6.1-6.5_

- [x] 9. Implement round-trip Excel verification
  - [x] 9.1 Create utility function to read and verify Excel files
    - Implement function to read Excel file using openpyxl
    - Parse header row and verify column order
    - Parse data rows starting from row 2
    - Return parsed data as list of dictionaries
    - _Requirements: 5.1-5.4_
  
  - [ ]* 9.2 Write property test for round-trip consistency
    - Generate random lists of transformed orders
    - Write to Excel then read back
    - Verify data equivalence (round-trip property)
    - _Requirements: 5.2_
  
  - [ ]* 9.3 Write unit tests for Excel reading
    - Test header row parsing
    - Test data row parsing
    - Test reading empty Excel (header only)
    - _Requirements: 5.3, 5.4_

- [x] 10. Final checkpoint and documentation
  - [x] 10.1 Verify all requirements and properties are satisfied
    - Run full test suite with pytest
    - Verify all property tests run minimum 100 iterations
    - Check test coverage meets goals (>90% line coverage, >85% branch coverage)
    - _Requirements: 7.1-7.11_
  
  - [x] 10.2 Create README with usage examples
    - Document how to install dependencies
    - Provide example usage of generate_logen_shipping_file function
    - Document environment variable configuration for access_token
    - Include example of running tests
  
  - [x] 10.3 Final checkpoint - Ensure all tests pass
    - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties using hypothesis
- Unit tests validate specific examples and edge cases using pytest
- All test files should be organized in tests/ folder
- Pay special attention to space handling in address concatenation (Property 3)
- Access token should be configurable via environment variable or function parameter
- Implement retry logic with exponential backoff for API failures
