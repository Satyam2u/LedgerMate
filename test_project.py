import pytest
from project import output_month, output_date, sorted_list_wrt_date, output_amount, person_exists


def test_output_month():
    # Test valid month indices in full (0) and short (1) formats
    assert output_month(1, 0) == "January"
    assert output_month(1, 1) == "Jan"
    assert output_month(8, 0) == "August"
    assert output_month(8, 1) == "Aug"
    assert output_month(12, 0) == "December"
    assert output_month(12, 1) == "Dec"


def test_output_date():
    # Test standard output date conversions
    assert output_date("2026-08-22", 0) == "22 August, 2026"
    assert output_date("2026-08-22", 1) == "22 Aug, 2026"
    assert output_date("2026-08-22", 2) == "22-08-2026"
    assert output_date("2026-08-22", 3) == "22/08/2026"


def test_sorted_list_wrt_date():
    records = [
        {"name": "Satyam", "date": "2026-08-25"},
        {"name": "Shivam", "date": "2026-08-10"},
        {"name": "Rahul", "date": "2026-08-18"},
    ]
    sorted_records = sorted_list_wrt_date(records)
    assert sorted_records[0]["name"] == "Shivam"
    assert sorted_records[1]["name"] == "Rahul"
    assert sorted_records[2]["name"] == "Satyam"


def test_output_amount():
    # Test currency prefix formatting
    res_1000 = output_amount(1000)
    assert res_1000.startswith("Rs. ")
    assert "1,000" in res_1000 or "1000" in res_1000

    res_50000 = output_amount(50000)
    assert res_50000.startswith("Rs. ")
    assert "50,000" in res_50000 or "50000" in res_50000


def test_person_exists():
    mock_persons = [
        {"name": "Shivam Sharma"},
        {"name": "Aman Verma"},
        {"name": "Pooja Singh"},
    ]
    # Direct name query
    status = person_exists(["Shivam Sharma", "Unknown Person"], mock_persons)
    assert "Shivam Sharma" in status[True]
    assert "Unknown Person" in status[False]

    # Special 'All' query
    all_status = person_exists(["All"], mock_persons)
    assert len(all_status[True]) == 3
    assert len(all_status[False]) == 0