"""
Referential integrity checks for the M5 datasets.
"""


def create_referential_result(
    check: str,
    status: str,
    message: str
) -> dict:
    """
    Create a standardized referential integrity result.
    """

    return {
        "check": check,
        "status": status,
        "message": message
    }