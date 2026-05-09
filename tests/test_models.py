import pytest
from core.models import Product

def test_product_brand_sanitization():
    # Test các brand cần chuẩn hoá đặc biệt
    p1 = Product(id="1", name="L1", brand="hp", price=100)
    assert p1.brand == "HP"
    
    p2 = Product(id="2", name="L2", brand="  macbook  ", price=200)
    assert p2.brand == "MacBook"
    
    p3 = Product(id="3", name="L3", brand="dell", price=300)
    assert p3.brand == "Dell" # Mặc định title()

def test_product_default_values():
    p = Product(id="1", name="Test", brand="Acer", price=50)
    assert p.currency == "VNĐ"
    assert p.category == []
    assert p.specs == {}
    assert p.stock == 0

def test_product_validation_error():
    # Kiểm tra pydantic bắt lỗi type
    with pytest.raises(Exception):
        # price phải là int
        Product(id="1", name="Test", brand="Acer", price="không có giá")
