# Requirements Document

## Introduction

This feature automates the process of fetching order data from Naver Smart Store and converting it into Logen delivery service's bulk shipping Excel format. The system eliminates manual data entry by bridging Naver's e-commerce platform with Logen's logistics system through API integration, data transformation, and Excel file generation.

## Glossary

- **Naver_Commerce_API**: The REST API provided by Naver Smart Store for accessing order data
- **API_Client**: The component that communicates with Naver Commerce API
- **Order_Transformer**: The component that converts Naver order data to Logen delivery format
- **Excel_Generator**: The component that creates Excel files in Logen's required format
- **Access_Token**: OAuth2 authentication token for Naver Commerce API
- **Payment_Status**: The payment state of an order (PAYED, CANCELED, etc.)
- **Shipping_Status**: The shipping state of an order (READY, DISPATCHED, DELIVERED, etc.)
- **Base_Address**: The primary address field from Naver orders
- **Detailed_Address**: The secondary address field from Naver orders (apartment number, etc.)
- **Full_Address**: The combined address field required by Logen format

## Requirements

### Requirement 1: Fetch Orders from Naver Smart Store

**User Story:** As a logistics coordinator, I want to fetch orders from Naver Smart Store, so that I can process them for Logen delivery.

#### Acceptance Criteria

1. WHEN the API_Client fetches orders, THE API_Client SHALL request only orders with Payment_Status equal to "PAYED"
2. WHEN the API_Client fetches orders, THE API_Client SHALL request only orders with Shipping_Status equal to "READY"
3. WHEN the Naver_Commerce_API returns a 401 status code, THE API_Client SHALL raise a NaverAPIError with authentication failure message
4. WHEN the Naver_Commerce_API returns a 5xx status code, THE API_Client SHALL retry the request up to 3 times with exponential backoff
5. WHEN all retry attempts fail, THE API_Client SHALL raise a NaverAPIError with the last error details
6. THE API_Client SHALL accept an Access_Token as a parameter for authentication

### Requirement 2: Transform Order Data to Logen Format

**User Story:** As a logistics coordinator, I want order data transformed to Logen's format, so that I can upload it to their bulk shipping system.

#### Acceptance Criteria

1. WHEN the Order_Transformer receives Naver order data, THE Order_Transformer SHALL copy the receiverName field directly to receiver_name
2. WHEN the Order_Transformer receives Naver order data, THE Order_Transformer SHALL concatenate Base_Address with a space and Detailed_Address to create Full_Address
3. WHEN the Order_Transformer receives Naver order data, THE Order_Transformer SHALL copy the receiverTel1 field directly to receiver_tel
4. WHEN the Order_Transformer receives Naver order data, THE Order_Transformer SHALL copy the productName field directly to product_name
5. WHEN the Order_Transformer receives Naver order data with a null deliveryMemo field, THE Order_Transformer SHALL use an empty string for delivery_memo
6. WHEN the Order_Transformer receives Naver order data with a non-null deliveryMemo field, THE Order_Transformer SHALL copy the deliveryMemo field directly to delivery_memo

### Requirement 3: Validate Required Order Fields

**User Story:** As a logistics coordinator, I want invalid orders to be rejected, so that I don't upload incomplete data to Logen.

#### Acceptance Criteria

1. IF an order is missing the receiverName field, THEN THE Order_Transformer SHALL raise a DataTransformError with the order ID and missing field name
2. IF an order is missing the Base_Address field, THEN THE Order_Transformer SHALL raise a DataTransformError with the order ID and missing field name
3. IF an order is missing the Detailed_Address field, THEN THE Order_Transformer SHALL raise a DataTransformError with the order ID and missing field name
4. IF an order is missing the receiverTel1 field, THEN THE Order_Transformer SHALL raise a DataTransformError with the order ID and missing field name
5. IF an order is missing the productName field, THEN THE Order_Transformer SHALL raise a DataTransformError with the order ID and missing field name

### Requirement 4: Generate Logen Excel File

**User Story:** As a logistics coordinator, I want an Excel file in Logen's format, so that I can upload it to their bulk shipping system.

#### Acceptance Criteria

1. WHEN the Excel_Generator creates a file, THE Excel_Generator SHALL name the file "로젠발송양식_{YYYYMMDD}.xlsx" where YYYYMMDD is the current date
2. WHEN the Excel_Generator creates a file, THE Excel_Generator SHALL create a header row with columns: "받는사람", "주소", "전화번호", "상품명", "배송메모"
3. WHEN the Excel_Generator receives N transformed orders, THE Excel_Generator SHALL create N data rows starting from row 2
4. WHEN the Excel_Generator creates a data row, THE Excel_Generator SHALL place receiver_name in column A
5. WHEN the Excel_Generator creates a data row, THE Excel_Generator SHALL place Full_Address in column B
6. WHEN the Excel_Generator creates a data row, THE Excel_Generator SHALL place receiver_tel in column C
7. WHEN the Excel_Generator creates a data row, THE Excel_Generator SHALL place product_name in column D
8. WHEN the Excel_Generator creates a data row, THE Excel_Generator SHALL place delivery_memo in column E
9. IF the Excel_Generator cannot create the file due to file system errors, THEN THE Excel_Generator SHALL raise an ExcelGenerationError with the file path and underlying error message

### Requirement 5: Parse and Pretty-Print Round-Trip for Excel Format

**User Story:** As a developer, I want to verify Excel file integrity, so that I can ensure data is correctly written and readable.

#### Acceptance Criteria

1. WHEN the Excel_Generator creates an Excel file, THE System SHALL be able to read the file back using openpyxl
2. FOR ALL valid transformed order lists, writing to Excel then reading from Excel SHALL produce equivalent data (round-trip property)
3. WHEN reading an Excel file, THE System SHALL parse the header row to verify column order matches the specification
4. WHEN reading an Excel file, THE System SHALL parse data rows starting from row 2

### Requirement 6: Main Function Integration

**User Story:** As a developer, I want a single function to execute the entire workflow, so that I can easily integrate this feature into other systems.

#### Acceptance Criteria

1. THE Main_Function SHALL accept an Access_Token as a parameter
2. WHERE an Access_Token is not provided as a parameter, THE Main_Function SHALL read the Access_Token from an environment variable
3. WHEN the Main_Function executes successfully, THE Main_Function SHALL return the path to the generated Excel file
4. WHEN any component raises an error, THE Main_Function SHALL propagate the error to the caller
5. THE Main_Function SHALL execute the workflow in order: fetch orders, transform data, generate Excel file

### Requirement 7: Property-Based Testing with Hypothesis

**User Story:** As a developer, I want comprehensive automated testing, so that I can verify correctness across all possible inputs.

#### Acceptance Criteria

1. THE Test_Suite SHALL include property-based tests using the hypothesis library
2. WHEN running property tests, THE Test_Suite SHALL execute a minimum of 100 iterations per property
3. THE Test_Suite SHALL verify Property 1: API status filtering with payment status "PAYED" and shipping status "READY"
4. THE Test_Suite SHALL verify Property 2: Direct field mapping preservation for receiverName, receiverTel1, and productName
5. THE Test_Suite SHALL verify Property 3: Address concatenation with space between Base_Address and Detailed_Address
6. THE Test_Suite SHALL verify Property 4: Filename date format matches "로젠발송양식_{YYYYMMDD}.xlsx"
7. THE Test_Suite SHALL verify Property 5: Excel row structure has header row plus N data rows for N orders
8. THE Test_Suite SHALL verify Property 6: API error propagation raises NaverAPIError
9. THE Test_Suite SHALL verify Property 7: Data validation error handling raises DataTransformError for missing required fields
10. THE Test_Suite SHALL be located in a tests/ folder
11. THE Test_Suite SHALL include unit tests using pytest for specific examples and edge cases
