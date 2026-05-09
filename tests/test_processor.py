import pytest
from core.models import Product
from ingestion.processor import product_to_text, product_to_metadata

@pytest.fixture
def sample_product():
    return Product(
        id="laptop-001",
        name="Dell XPS 13 9315",
        brand="Dell",
        price=25000000,
        category=["hoctap_vanphong"],
        specs={
            "cpu": "Intel Core i5-1230U",
            "ram": "16GB",
            "gpu": "Intel Iris Xe",
            "storage": "512GB SSD",
            "screen": "13.4 inch FHD+"
        },
        description="Laptop văn phòng cao cấp, mỏng nhẹ."
    )

def test_product_to_text(sample_product):
    text = product_to_text(sample_product)
    
    # Kiểm tra các thông tin quan trọng có trong text không
    assert "Dell XPS 13 9315" in text
    assert "Intel Core i5-1230U" in text
    assert "16GB" in text
    assert "Học tập / Văn phòng" in text # Check category mapping
    assert "25000000" not in text # Giá không nên nằm trong searchable text

def test_product_to_metadata(sample_product):
    meta = product_to_metadata(sample_product)
    
    assert meta["product_id"] == "laptop-001"
    assert meta["brand"] == "Dell"
    assert meta["price"] == 25000000
    assert meta["stock"] == 0
    assert "hoctap_vanphong" in meta["category"]
    
    # Kiểm tra việc tách từ (tokenization) cho BM25
    assert "segmented_text" in meta
    assert isinstance(meta["segmented_text"], str)
    assert len(meta["segmented_text"]) > 0
