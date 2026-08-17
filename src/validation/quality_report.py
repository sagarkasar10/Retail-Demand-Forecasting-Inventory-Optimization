from datetime import datetime


def create_quality_report(
    sales_df,
    calendar_df,
    prices_df
) -> dict:
    """
    Create a final Week 1 data quality report.
    """

    report = {
        "generated_at": datetime.now().isoformat(),

        "sales": {
            "rows": len(sales_df),
            "columns": len(sales_df.columns),
            "null_ids": int(
                sales_df["id"].isna().sum()
            ),
            "null_items": int(
                sales_df["item_id"].isna().sum()
            ),
            "null_stores": int(
                sales_df["store_id"].isna().sum()
            ),
        },

        "calendar": {
            "rows": len(calendar_df),
            "columns": len(calendar_df.columns),
            "null_dates": int(
                calendar_df["date"].isna().sum()
            ),
            "unique_dates": int(
                calendar_df["date"].nunique()
            ),
        },

        "prices": {
            "rows": len(prices_df),
            "columns": len(prices_df.columns),
            "null_prices": int(
                prices_df["sell_price"].isna().sum()
            ),
            "negative_prices": int(
                (
                    prices_df["sell_price"] < 0
                ).sum()
            ),
        }
    }

    return report


def print_quality_report(
    report: dict
) -> None:
    """
    Print the final Week 1 data quality report.
    """

    print("\n")
    print("=" * 70)
    print("WEEK 1 FINAL DATA QUALITY REPORT")
    print("=" * 70)

    print(
        f"\nGenerated at: "
        f"{report['generated_at']}"
    )

    # --------------------------------------------------------
    # SALES
    # --------------------------------------------------------

    print("\nSALES DATA")
    print("-" * 40)

    print(
        f"Rows        : "
        f"{report['sales']['rows']:,}"
    )

    print(
        f"Columns     : "
        f"{report['sales']['columns']:,}"
    )

    print(
        f"NULL IDs    : "
        f"{report['sales']['null_ids']:,}"
    )

    print(
        f"NULL items  : "
        f"{report['sales']['null_items']:,}"
    )

    print(
        f"NULL stores : "
        f"{report['sales']['null_stores']:,}"
    )

    # --------------------------------------------------------
    # CALENDAR
    # --------------------------------------------------------

    print("\nCALENDAR DATA")
    print("-" * 40)

    print(
        f"Rows          : "
        f"{report['calendar']['rows']:,}"
    )

    print(
        f"Columns       : "
        f"{report['calendar']['columns']:,}"
    )

    print(
        f"NULL dates    : "
        f"{report['calendar']['null_dates']:,}"
    )

    print(
        f"Unique dates  : "
        f"{report['calendar']['unique_dates']:,}"
    )

    # --------------------------------------------------------
    # PRICES
    # --------------------------------------------------------

    print("\nPRICING DATA")
    print("-" * 40)

    print(
        f"Rows             : "
        f"{report['prices']['rows']:,}"
    )

    print(
        f"Columns          : "
        f"{report['prices']['columns']:,}"
    )

    print(
        f"NULL prices      : "
        f"{report['prices']['null_prices']:,}"
    )

    print(
        f"Negative prices  : "
        f"{report['prices']['negative_prices']:,}"
    )

    print("\n" + "=" * 70)


def quality_report_passed(
    report: dict
) -> bool:
    """
    Determine whether the final Week 1 quality report passes.
    """

    sales_passed = (
        report["sales"]["null_ids"] == 0
        and
        report["sales"]["null_items"] == 0
        and
        report["sales"]["null_stores"] == 0
    )

    calendar_passed = (
        report["calendar"]["null_dates"] == 0
        and
        report["calendar"]["unique_dates"] > 0
    )

    prices_passed = (
        report["prices"]["null_prices"] == 0
        and
        report["prices"]["negative_prices"] == 0
    )

    passed = (
        sales_passed
        and calendar_passed
        and prices_passed
    )

    if passed:
        print(
            "\n✓ FINAL DATA QUALITY REPORT: PASS"
        )
    else:
        print(
            "\n✗ FINAL DATA QUALITY REPORT: FAIL"
        )

    return passed