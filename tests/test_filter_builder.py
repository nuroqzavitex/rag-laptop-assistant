import pytest
from retriever.filter_builder import build_where_clause, build_metadata_filter, post_filter_results

def test_build_where_clause_empty():
    # Không có intent nào liên quan đến Qdrant DB thì trả về None
    assert build_where_clause({}) is None

def test_build_where_clause_single():
    # Nếu chỉ có 1 điều kiện lọc
    intent = {"brand": "Asus"}
    clause = build_where_clause(intent)
    assert clause == {"brand": {"$eq": "Asus"}}

def test_build_where_clause_multiple():
    # Nếu có nhiều điều kiện, nó phải gom lại bằng toán tử $and
    intent = {
        "brand": "Lenovo",
        "category": "gaming",
        "price_min": 20000000
    }
    clause = build_where_clause(intent)
    assert "$and" in clause
    assert len(clause["$and"]) == 3
    assert {"brand": {"$eq": "Lenovo"}} in clause["$and"]
    assert {"category": {"$contains": "gaming"}} in clause["$and"]
    assert {"price": {"$gte": 20000000}} in clause["$and"]

def test_build_metadata_filter():
    # Kiểm tra build metadata filter cho việc lọc bằng tay (không dùng DB)
    intent = {"gpu": "RTX 4060", "ram_size": 16}
    filters = build_metadata_filter(intent)
    assert filters == {"gpu_keyword": "RTX 4060", "ram_size": 16}

def test_post_filter_results():
    # Mock data kết quả trả về từ DB
    results = [
        {"id": 1, "metadata": {"gpu": "Nvidia RTX 4060", "ram": "16 GB"}},
        {"id": 2, "metadata": {"gpu": "Nvidia RTX 3050", "ram": "8 GB"}},
        {"id": 3, "metadata": {"gpu": "RTX 4060 Ti", "ram": "32 GB"}},
    ]
    
    # 1. Test lọc GPU (string match)
    meta_filter = {"gpu_keyword": "RTX 4060"}
    filtered = post_filter_results(results, meta_filter)
    assert len(filtered) == 2
    assert filtered[0]["id"] == 1
    assert filtered[1]["id"] == 3

    # 2. Test lọc RAM (phải parse string thành số rồi so sánh >=)
    meta_filter = {"ram_size": 16}
    filtered = post_filter_results(results, meta_filter)
    assert len(filtered) == 2
    assert filtered[0]["id"] == 1
    assert filtered[1]["id"] == 3

    # 3. Test lọc ổ cứng (phải so sánh sau khi đưa về cùng đơn vị GB)
    storage_results = [
        {"id": 1, "metadata": {"storage": "SSD 512GB"}},
        {"id": 2, "metadata": {"storage": "SSD 1TB"}},
        {"id": 3, "metadata": {"storage": "2TB"}},
        {"id": 4, "metadata": {"storage": "SSD 256GB"}},
    ]
    meta_filter = {"storage_tb": 1} # Yêu cầu 1TB (1024GB) trở lên
    filtered = post_filter_results(storage_results, meta_filter)
    assert len(filtered) == 2
    assert filtered[0]["id"] == 2
    assert filtered[1]["id"] == 3

    # 4. Test fallback: Nếu lọc không ra kết quả nào, phải giữ nguyên danh sách cũ
    meta_filter = {"ram_size": 64}
    filtered = post_filter_results(results, meta_filter)
    assert len(filtered) == 3 

    # Test fallback cho ổ cứng
    meta_filter = {"storage_tb": 4}
    filtered = post_filter_results(storage_results, meta_filter)
    assert len(filtered) == 4 
