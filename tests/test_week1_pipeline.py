import pandas as pd
import pytest

from src.validation.sales_quality import (
    clean_sales_data,
)

from src.validation.pricing_quality import (
    clean_pricing_data,
)

from src.validation.calendar_quality import (
    clean_calendar_data,
)

from src.validation.pipeline_validation import (
    validate_sales_dataframe,
    validate_calendar_dataframe,
    validate_price_dataframe,
)

def test_sales_negative_values_are_rejected():

    df = create_sales_test_data()

    df["d_1"] = [-10]

    with pytest.raises(ValueError):
        clean_sales_data(df)


def test_sales_null_values_are_rejected():

    df = create_sales_test_data()

    df["d_1"] = [None]

    with pytest.raises(ValueError):
        clean_sales_data(df)


def test_duplicate_sales_ids_are_detected():

    df = pd.concat(
        [
            create_sales_test_data(),
            create_sales_test_data(),
        ],
        ignore_index=True,
    )

    from src.validation.pipeline_validation import (
        validate_sales_dataframe,
    )

    with pytest.raises(ValueError):
        validate_sales_dataframe(df)


def test_negative_price_is_rejected():

    df = create_price_test_data()

    df["sell_price"] = [-5]

    with pytest.raises(ValueError):
        clean_pricing_data(df)


def test_invalid_calendar_month_is_rejected():

    df = create_calendar_test_data()

    df["month"] = [13]

    with pytest.raises(ValueError):
        clean_calendar_data(df)


def test_invalid_calendar_weekday_is_rejected():

    df = create_calendar_test_data()

    df["wday"] = [8]

    with pytest.raises(ValueError):
        clean_calendar_data(df)


def create_sales_test_data():
    return pd.DataFrame({
        "id": ["item_1_store_1"],
        "item_id": ["ITEM_1"],
        "dept_id": ["DEPT_1"],
        "cat_id": ["CAT_1"],
        "store_id": ["STORE_1"],
        "state_id": ["CA"],
        "d_1": [10],
        "d_2": [12],
    })


def create_calendar_test_data():
    return pd.DataFrame({
        "date": pd.to_datetime(
            ["2011-01-29"]
        ),
        "wm_yr_wk": [11101],
        "weekday": ["Saturday"],
        "wday": [1],
        "month": [1],
        "year": [2011],
    })


def create_price_test_data():
    return pd.DataFrame({
        "store_id": ["STORE_1"],
        "item_id": ["ITEM_1"],
        "wm_yr_wk": [11101],
        "sell_price": [10.50],
    })


def test_sales_validation():

    df = create_sales_test_data()

    assert (
        validate_sales_dataframe(df)
        is True
    )


def test_calendar_validation():

    df = create_calendar_test_data()

    assert (
        validate_calendar_dataframe(df)
        is True
    )


def test_price_validation():

    df = create_price_test_data()

    assert (
        validate_price_dataframe(df)
        is True
    )


def test_sales_required_columns():

    df = create_sales_test_data()

    assert "id" in df.columns
    assert "item_id" in df.columns
    assert "store_id" in df.columns


def test_calendar_required_columns():

    df = create_calendar_test_data()

    assert "date" in df.columns
    assert "wm_yr_wk" in df.columns
    assert "month" in df.columns
    assert "year" in df.columns


def test_price_required_columns():

    df = create_price_test_data()

    assert "store_id" in df.columns
    assert "item_id" in df.columns
    assert "wm_yr_wk" in df.columns
    assert "sell_price" in df.columns

