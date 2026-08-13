"""
Data quality validation functions.

Detailed checks will be implemented during Week 1.
"""


def create_quality_result(
    dataset: str,
    check: str,
    status: str,
    message: str
) -> dict:
    """
    Create a standardized data quality result.
    """

    return {
        "dataset": dataset,
        "check": check,
        "status": status,
        "message": message
    }


def print_quality_results(results: list[dict]) -> None:
    """
    Print validation results in a readable format.
    """

    print("\n" + "=" * 70)
    print("DATA QUALITY RESULTS")
    print("=" * 70)

    for result in results:
        print(
            f"[{result['status']}] "
            f"{result['dataset']} | "
            f"{result['check']} | "
            f"{result['message']}"
        )

    print("=" * 70)