import pytest
from jobwatcher.rules import in_role


@pytest.mark.parametrize("title", [
    "Marketing Data Analyst", "Senior Growth Analyst", "Analyst, Performance Marketing",
    "Marketing Analytics Lead", "Lifecycle Marketing Insights Manager", "CRM Data Scientist",
    "Brand Measurement Analyst"])
def test_in_role(title):
    assert in_role(title)


@pytest.mark.parametrize("title", [
    "Software Engineer", "Marketing Manager", "Financial Analyst", "Data Analyst",
    "Account Executive", "", None, "Semiconductor Analyst"])
def test_not_in_role(title):
    assert not in_role(title)
