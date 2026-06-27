def is_mock_key(key: str) -> bool:
    if not key:
        return False
    key_str = str(key).strip().lower()
    return (
        key_str.startswith("mock_") or 
        key_str.startswith("test_") or 
        key_str.startswith("sk-test") or 
        key_str == "sk-123" or
        "mock" in key_str or
        "test" in key_str
    )
