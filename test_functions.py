import pandas as pd
from app import (
    getMissionCountByCompany,
    getSuccessRate,
    getMissionsByDateRange,
    getTopCompaniesByMissionCount,
    getMissionStatusCount,
    getMissionsByYear,
    getMostUsedRocket,
    getAverageMissionsPerYear
)

# Function 1
def test_getMissionCountByCompany_normal():
    assert getMissionCountByCompany("NASA") == 203

def test_getMissionCountByCompany_empty():
    assert getMissionCountByCompany("") == 0

def test_getMissionCountByCompany_nonexistent():
    assert getMissionCountByCompany("Fake Company") == 0

def test_getMissionCountByCompany_wrong_case():
    assert getMissionCountByCompany("nasa") == 0

# Function 2
def test_getSuccessRate_normal():
    assert getSuccessRate("NASA") == 91.63

def test_getSuccessRate_nonexistent():
    assert getSuccessRate("Fake Company") == 0.0

def test_getSuccessRate_empty():
    assert getSuccessRate("") == 0.0

# Function 3
def test_getMissionsByDateRange_normal():
    assert getMissionsByDateRange("1957-10-01", "1957-12-31") == ["Sputnik-1", "Sputnik-2", "Vanguard TV3"]

def test_getMissionsByDateRange_invalid_format():
    assert getMissionsByDateRange("not-a-date", "2020-01-01") == []

def test_getMissionsByDateRange_end_before_start():
    assert getMissionsByDateRange("1957-12-31", "1957-10-01") == []

def test_getMissionsByDateRange_empty():
    assert getMissionsByDateRange("", "") == []

# Function 4
def test_getTopCompaniesByMissionCount_normal():
    assert getTopCompaniesByMissionCount(3) == [("RVSN USSR", 1777), ("CASC", 338), ("Arianespace", 293)]

def test_getTopCompaniesByMissionCount_zero():
    assert getTopCompaniesByMissionCount(0) == []

def test_getTopCompaniesByMissionCount_negative():
    assert getTopCompaniesByMissionCount(-1) == []

# Function 5
def test_getMissionStatusCount_normal():
    result = getMissionStatusCount()
    assert result["Success"] == 4162
    assert result["Failure"] == 357
    assert result["Partial Failure"] == 107
    assert result["Prelaunch Failure"] == 4

# Function 6
def test_getMissionsByYear_normal():
    assert getMissionsByYear(2020) == 119

def test_getMissionsByYear_no_missions():
    assert getMissionsByYear(1950) == 0

def test_getMissionsByYear_future():
    assert getMissionsByYear(2099) == 0

# Function 7
def test_getMostUsedRocket_normal():
    assert getMostUsedRocket() == "Cosmos-3M (11K65M)"

# Function 8
def test_getAverageMissionsPerYear_normal():
    assert getAverageMissionsPerYear(2010, 2020) == 72.27

def test_getAverageMissionsPerYear_same_year():
    assert getAverageMissionsPerYear(2020, 2020) == 119.0

def test_getAverageMissionsPerYear_end_before_start():
    assert getAverageMissionsPerYear(2020, 2010) == 0.0

def test_getAverageMissionsPerYear_no_missions():
    assert getAverageMissionsPerYear(1950, 1950) == 0.0
