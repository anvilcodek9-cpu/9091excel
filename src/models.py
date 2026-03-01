"""Data models for Naver-Logen integration."""

from dataclasses import dataclass


@dataclass
class NaverOrder:
    """
    Naver Commerce API order structure.
    
    Represents the data structure from Naver Commerce API with all required
    fields for order processing and delivery information.
    
    Attributes:
        order_id: Unique identifier for the order
        product_order_id: Unique identifier for the product within the order
        receiver_name: Name of the recipient (receiverName in API)
        base_address: Primary address field (baseAddress in API)
        detailed_address: Secondary address field like apartment number (detailedAddress in API)
        receiver_tel1: Primary phone number of the recipient (receiverTel1 in API)
        product_name: Name of the product (productName in API)
        delivery_memo: Delivery instructions or notes (deliveryMemo in API)
        payment_status: Payment state (PAYED, CANCELED, etc.)
        shipping_status: Shipping state (READY, DISPATCHED, DELIVERED, etc.)
    """
    order_id: str
    product_order_id: str
    receiver_name: str
    base_address: str
    detailed_address: str
    receiver_tel1: str
    product_name: str
    delivery_memo: str
    payment_status: str
    shipping_status: str


@dataclass
class LogenShipment:
    """
    Logen delivery Excel format structure.
    
    Represents the transformed data structure for Logen delivery format,
    matching the columns required in Logen's bulk shipping Excel file.
    
    Attributes:
        receiver_name: Name of the recipient (Column A: 받는사람)
        full_address: Complete address combining base and detailed address (Column B: 주소)
        receiver_tel: Phone number of the recipient (Column C: 전화번호)
        product_name: Name of the product (Column D: 상품명)
        delivery_memo: Delivery instructions or notes (Column E: 배송메모)
    """
    receiver_name: str
    full_address: str
    receiver_tel: str
    product_name: str
    delivery_memo: str
