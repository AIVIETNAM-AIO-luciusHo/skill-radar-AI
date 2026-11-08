from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from skillradar.ports.schemas import (
    MarketRegion,
    Polarity,
    RawJD,
    SalaryBand,
    SalaryBoundType,
    SalaryPeriod,
    SectionSource,
    SkillMention,
)

NOW = datetime(2026, 11, 8, tzinfo=UTC)


def jd(**kw):
    base = dict(
        job_id="j1",
        source_dataset="Greenhouse_API",
        market_region=MarketRegion.GLOBAL,
        title="Backend Engineer",
        description="We use C++ and Node.js.",
        ingested_at=NOW,
    )
    return RawJD(**{**base, **kw})


def mention(**kw):
    base = dict(
        mention_id="m1",
        job_id="j1",
        skill_id="cpp",
        section_source=SectionSource.REQUIREMENTS,
        char_start=3,
        char_end=6,
        evidence_span="use",
        polarity=Polarity.REQUIRED,
        link_confidence=1.0,
        model_version="dict_v1",
    )
    return SkillMention(**{**base, **kw})


def test_rawjd_valid_minimal():
    assert jd().salary is None


@pytest.mark.parametrize("field", ["job_id", "title", "description", "source_dataset"])
def test_rawjd_rejects_empty_required_text(field):
    with pytest.raises(ValidationError):
        jd(**{field: ""})


def test_rawjd_rejects_unknown_field():
    with pytest.raises(ValidationError):
        jd(salary_usd=1)


def test_rawjd_last_seen_before_first_seen():
    with pytest.raises(ValidationError):
        jd(first_seen=NOW, last_seen=datetime(2026, 1, 1, tzinfo=UTC))


def test_salary_range_ok_and_disclosed():
    s = SalaryBand(
        bound_type=SalaryBoundType.RANGE,
        min_amount=1500,
        max_amount=2500,
        currency="USD",
        period=SalaryPeriod.MONTH,
    )
    assert s.disclosed


def test_salary_none_is_not_disclosed():
    assert not SalaryBand().disclosed  # "Thoả thuận" / "Competitive": never imputed


def test_salary_predicted_is_not_disclosed():
    s = SalaryBand(
        bound_type=SalaryBoundType.RANGE,
        min_amount=1,
        max_amount=2,
        currency="USD",
        period=SalaryPeriod.YEAR,
        is_predicted=True,
    )
    assert not s.disclosed


def test_salary_upper_only_keeps_bound_type():
    s = SalaryBand(
        bound_type=SalaryBoundType.UPPER_ONLY,
        max_amount=3000,
        currency="USD",
        period=SalaryPeriod.MONTH,
    )
    assert s.disclosed and s.min_amount is None


@pytest.mark.parametrize(
    "kw",
    [
        dict(bound_type=SalaryBoundType.RANGE, min_amount=1, currency="USD", period="YEAR"),
        dict(bound_type=SalaryBoundType.UPPER_ONLY, min_amount=1, currency="USD", period="YEAR"),
        dict(bound_type=SalaryBoundType.NONE, max_amount=5),
        dict(
            bound_type=SalaryBoundType.RANGE,
            min_amount=9,
            max_amount=1,
            currency="USD",
            period="YEAR",
        ),
        dict(bound_type=SalaryBoundType.RANGE, min_amount=1, max_amount=2, period="YEAR"),
        dict(
            bound_type=SalaryBoundType.RANGE,
            min_amount=0,
            max_amount=2,
            currency="USD",
            period="YEAR",
        ),
        dict(
            bound_type=SalaryBoundType.RANGE,
            min_amount=1,
            max_amount=2,
            currency="usd",
            period="YEAR",
        ),
    ],
)
def test_salary_invalid(kw):
    with pytest.raises(ValidationError):
        SalaryBand(**kw)


def test_mention_valid_and_matches_text():
    m = mention()
    assert m.matches("We use C++ and Node.js.")
    assert not m.matches("We  use C++")  # shifted offsets must be detected


def test_mention_special_char_skill():
    text = "Experience with C++ and Node.js"
    m = mention(char_start=16, char_end=19, evidence_span="C++")
    assert m.matches(text)


@pytest.mark.parametrize(
    "kw",
    [
        dict(char_start=5, char_end=5),
        dict(char_start=-1, char_end=3, evidence_span="abc"),
        dict(char_start=3, char_end=6, evidence_span="used"),  # length mismatch
        dict(polarity="MAYBE"),
        dict(link_confidence=1.5),
        dict(model_version=""),
    ],
)
def test_mention_invalid(kw):
    with pytest.raises(ValidationError):
        mention(**kw)
