"""Pydantic v2 data contracts shared by every pipeline stage (see docs/technical-report.md §3.3).

`RawJD` is the bronze row, `SalaryBand` the parsed salary, `SkillMention` the silver evidence row.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Polarity(StrEnum):
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"
    NEGATED = "NEGATED"


class SectionSource(StrEnum):
    REQUIREMENTS = "REQUIREMENTS"
    RESPONSIBILITIES = "RESPONSIBILITIES"


class MarketRegion(StrEnum):
    GLOBAL = "GLOBAL"
    US = "US"
    EU = "EU"
    VN = "VN"  # Phase 3


class SalaryPeriod(StrEnum):
    HOUR = "HOUR"
    DAY = "DAY"
    MONTH = "MONTH"
    YEAR = "YEAR"


class SalaryBoundType(StrEnum):
    RANGE = "RANGE"
    UPPER_ONLY = "UPPER_ONLY"  # "Up to X": never enters the main quantiles
    LOWER_ONLY = "LOWER_ONLY"
    NONE = "NONE"  # "Thoả thuận" / "Competitive": salary_disclosed=False, never imputed


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SalaryBand(_Strict):
    """Salary exactly as parsed from the source, before currency/period normalisation."""

    bound_type: SalaryBoundType = SalaryBoundType.NONE
    min_amount: float | None = Field(default=None, gt=0)
    max_amount: float | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    period: SalaryPeriod | None = None
    is_predicted: bool = False  # platform-estimated salary: excluded from quantiles

    @model_validator(mode="after")
    def _consistent(self) -> SalaryBand:
        has_min, has_max = self.min_amount is not None, self.max_amount is not None
        expected = {
            SalaryBoundType.RANGE: (True, True),
            SalaryBoundType.UPPER_ONLY: (False, True),
            SalaryBoundType.LOWER_ONLY: (True, False),
            SalaryBoundType.NONE: (False, False),
        }[self.bound_type]
        if (has_min, has_max) != expected:
            raise ValueError(f"bound_type={self.bound_type} inconsistent with min/max amounts")
        if has_min and has_max and self.min_amount > self.max_amount:
            raise ValueError("min_amount must be <= max_amount")
        if self.bound_type is not SalaryBoundType.NONE and not (self.currency and self.period):
            raise ValueError("currency and period are required when an amount is present")
        return self

    @property
    def disclosed(self) -> bool:
        """True only for a real (non-predicted) salary; the basis of `salary_disclosed`."""
        return self.bound_type is not SalaryBoundType.NONE and not self.is_predicted


class RawJD(_Strict):
    """One job posting as stored in bronze (immutable)."""

    job_id: str = Field(min_length=1)
    source_dataset: str = Field(min_length=1)
    market_region: MarketRegion
    title: str = Field(min_length=1)
    company: str | None = None
    description: str = Field(min_length=1)  # original text; offsets refer to this string
    posted_date: date | None = None
    first_seen: datetime | None = None  # only live-crawled sources have these (ghost filter)
    last_seen: datetime | None = None
    salary: SalaryBand | None = None
    ingested_at: datetime

    @model_validator(mode="after")
    def _seen_order(self) -> RawJD:
        if self.first_seen and self.last_seen and self.last_seen < self.first_seen:
            raise ValueError("last_seen must be >= first_seen")
        return self


class SkillMention(_Strict):
    """One skill occurrence with the evidence needed to trace any statistic back to the text."""

    mention_id: str = Field(min_length=1)
    job_id: str = Field(min_length=1)
    skill_id: str = Field(min_length=1)
    section_source: SectionSource
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    evidence_span: str = Field(min_length=1)
    polarity: Polarity
    link_confidence: float = Field(ge=0.0, le=1.0)
    model_version: str = Field(min_length=1)  # e.g. dict_v1, deberta_v3_onnx

    @model_validator(mode="after")
    def _span(self) -> SkillMention:
        if self.char_end <= self.char_start:
            raise ValueError("char_end must be > char_start")
        if len(self.evidence_span) != self.char_end - self.char_start:
            raise ValueError("evidence_span length must equal char_end - char_start")
        return self

    def matches(self, text: str) -> bool:
        """Constitution I: the span must reproduce exactly from the original job text."""
        return text[self.char_start : self.char_end] == self.evidence_span
