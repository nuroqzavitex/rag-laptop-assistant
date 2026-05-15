import pytest
from retriever.intent_parser import parse_intent, is_company_query

def test_parse_intent_brand():
    # Kiểm tra nhận diện đúng thương hiệu (cả viết hoa/thường)
    intent = parse_intent("tôi muốn mua laptop lenovo")
    assert intent.get("brand") == "Lenovo"

    intent = parse_intent("macbook pro m3")
    assert intent.get("brand") == "MacBook"

def test_parse_intent_category():
    # Kiểm tra nhận diện đúng loại nhu cầu/category
    intent = parse_intent("tìm laptop gaming để chơi game")
    assert intent.get("category") == "gaming"

    intent = parse_intent("laptop làm đồ họa")
    assert intent.get("category") == "dohoa"

def test_parse_intent_price_range():
    # Kiểm tra parse giá dạng khoảng (từ A đến B)
    intent = parse_intent("giá từ 20 đến 30 triệu")
    assert intent.get("price_min") == 20000000
    assert intent.get("price_max") == 30000000

    # Kiểm tra parse giá dạng có số thập phân
    intent = parse_intent("20.5-30.5 triệu")
    assert intent.get("price_min") == 20500000
    assert intent.get("price_max") == 30500000

def test_parse_intent_price_max_min():
    # Kiểm tra parse giá trần (dưới X)
    intent = parse_intent("dưới 15 triệu")
    assert intent.get("price_max") == 15000000

    # Kiểm tra parse giá sàn (trên X)
    intent = parse_intent("trên 50.5 triệu")
    assert intent.get("price_min") == 50500000

def test_parse_intent_price_around():
    # Kiểm tra parse giá ước lượng (khoảng/tầm/rơi vào X) -> ±20%
    intent = parse_intent("khoảng 20 triệu")
    assert intent.get("price_min") == 16000000  # 20 * 0.8
    assert intent.get("price_max") == 24000000  # 20 * 1.2

    intent = parse_intent("laptop 30tr")
    assert intent.get("price_min") == 24000000
    assert intent.get("price_max") == 36000000

def test_parse_intent_gpu_cpu_ram():
    # Kiểm tra nhận diện phần cứng
    intent = parse_intent("rtx 4060 core i7 ram 16gb")
    assert intent.get("gpu") == "RTX 4060"
    assert intent.get("cpu") == "core i7"
    assert intent.get("ram_size") == 16

def test_parse_intent_combined():
    # Kiểm tra một câu truy vấn phức tạp kết hợp nhiều intent
    intent = parse_intent("dell gaming dưới 30 triệu rtx 4050")
    assert intent.get("brand") == "Dell"
    assert intent.get("category") == "gaming"
    assert intent.get("price_max") == 30000000
    assert intent.get("gpu") == "RTX 4050"

def test_is_company_query():
    assert is_company_query("Shop ở đâu?") is True
    assert is_company_query("Chính sách bảo hành như thế nào?") is True
    assert is_company_query("Giờ mở cửa của shop") is True

def test_is_company_query_not_when_product_intent():
    assert is_company_query("Laptop gaming dưới 30 triệu") is False
    assert is_company_query("Shop có laptop dell không") is False
    assert is_company_query("Macbook pro m3 giá bao nhiêu") is False
