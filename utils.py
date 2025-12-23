def validate_api_key(provided_key: str, real_key: str) -> bool:
    """
    Compare the provided API key with the real API key.
    Returns True if keys match.
    """
    if not provided_key:
        return False
    return provided_key == real_key
