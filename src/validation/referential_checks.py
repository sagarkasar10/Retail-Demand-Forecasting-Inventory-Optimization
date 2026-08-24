def create_referential_result(
    check_name: str,
    passed: bool,
    invalid_count: int,
) -> dict:
    """
    Create a standardized referential integrity result.
    """

    return {
        "check_name": check_name,
        "passed": passed,
        "invalid_count": invalid_count,
    }