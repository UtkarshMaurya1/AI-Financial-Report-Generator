from pydantic import BaseModel, Field
from typing import Optional

class ShareholdingEntry(BaseModel):
    period: str
    promoters: Optional[float] = None
    fii: Optional[float] = None
    mf_institutions: Optional[float] = None
    public: Optional[float] = None
    others: Optional[float] = None

class PricePerformanceEntry(BaseModel):
    period: str                     # "3 Month" / "6 Month" / "1 Year"
    absolute_return: Optional[float] = None
    absolute_benchmark: Optional[float] = None
    relative_return: Optional[float] = None

class QuarterlyFinancialEntry(BaseModel):
    metric: str                     # "Sales", "EBITDA", "Margin (%)", etc.
    current_quarter: Optional[float] = None
    yoy_quarter: Optional[float] = None
    yoy_growth_pct: Optional[float] = None
    prev_quarter: Optional[float] = None
    qoq_growth_pct: Optional[float] = None

class AnnualFinancialEntry(BaseModel):
    metric: str
    fy_minus_2: Optional[float] = None
    fy_minus_1: Optional[float] = None
    fy_current: Optional[float] = None
    fy_plus_1: Optional[float] = None
    fy_plus_2: Optional[float] = None

class RatioEntry(BaseModel):
    category: str                   # "Profitability", "Liquidity", "Valuation", etc.
    metric: str
    values: dict[str, Optional[float]] = Field(default_factory=dict)  # {"FY23A": 6.1, ...}


class ChartSeries(BaseModel):
    labels: list[str] = Field(default_factory=list)      # ["Q2FY24", "Q3FY24", ...]
    values: list[Optional[float]] = Field(default_factory=list)   # absolute value bars
    margin_or_growth: list[Optional[float]] = Field(default_factory=list)  # line overlay


class CompanyInfo(BaseModel):
    company_name: Optional[str] = None
    sector: Optional[str] = None
    rating: Optional[str] = None            # BUY/HOLD/REDUCE
    target_price: Optional[float] = None
    cmp: Optional[float] = None
    expected_return_pct: Optional[float] = None
    report_date: Optional[str] = None
    stock_type: Optional[str] = None        # Large/Mid/Small cap
    nse_code: Optional[str] = None
    bse_code: Optional[str] = None
    bloomberg_code: Optional[str] = None
    time_frame: Optional[str] = None


class CompanyData(BaseModel):
    market_cap: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    enterprise_value: Optional[float] = None
    outstanding_shares: Optional[float] = None
    free_float_pct: Optional[float] = None
    dividend_yield_pct: Optional[float] = None
    avg_volume_6m: Optional[float] = None
    beta: Optional[float] = None
    face_value: Optional[float] = None


class Financials(BaseModel):
    shareholding: list[ShareholdingEntry] = Field(default_factory=list)
    price_performance: list[PricePerformanceEntry] = Field(default_factory=list)
    quarterly: list[QuarterlyFinancialEntry] = Field(default_factory=list)
    annual: list[AnnualFinancialEntry] = Field(default_factory=list)
    ratios: list[RatioEntry] = Field(default_factory=list)


class Charts(BaseModel):
    revenue: Optional[ChartSeries] = None
    ebitda: Optional[ChartSeries] = None
    pat: Optional[ChartSeries] = None
    gross_order_value: Optional[ChartSeries] = None

    # chart image pathss
    revenue_chart_path: Optional[str] = None 
    ebitda_chart_path: Optional[str] = None
    pat_chart_path: Optional[str] = None
    gov_chart_path: Optional[str] = None


class ReportSchema(BaseModel):
    company: CompanyInfo = Field(default_factory=CompanyInfo)
    company_data: CompanyData = Field(default_factory=CompanyData)
    financials: Financials = Field(default_factory=Financials)
    charts: Charts = Field(default_factory=Charts)
    highlights: list[str] = Field(default_factory=list)
    outlook: Optional[str] = None
    valuation: Optional[str] = None