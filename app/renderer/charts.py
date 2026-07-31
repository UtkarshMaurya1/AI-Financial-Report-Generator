import os
import matplotlib
matplotlib.use("Agg")  # no GUI backend needed
import matplotlib.pyplot as plt

from app.schemas.report_schema import QuarterlyFinancialEntry, ChartSeries, Charts

CHART_OUTPUT_DIR = "app/static/charts"


def build_chart_series(quarterly: list[QuarterlyFinancialEntry], metric_name: str, margin_metric: str | None = None) -> ChartSeries | None:
    """
    Builds a ChartSeries from quarterly entries for a given metric.
    NOTE: Geojit's Revenue/EBITDA/PAT charts show trend across many quarters
    (Q2FY24...Q1FY26), but our quarterly extractor only captures the
    current + YoY + prior quarter (4 data points max) per the source report.
    This function works with whatever quarters are available.
    """
    entry = next((e for e in quarterly if e.metric.strip().lower() == metric_name.lower()), None)
    if not entry:
        return None

    labels, values = [], []
    if entry.yoy_quarter is not None:
        labels.append("YoY Qtr")
        values.append(entry.yoy_quarter)
    if entry.prev_quarter is not None:
        labels.append("Prev Qtr")
        values.append(entry.prev_quarter)
    if entry.current_quarter is not None:
        labels.append("Current Qtr")
        values.append(entry.current_quarter)

    if not values:
        return None

    margin_values = []
    if margin_metric:
        margin_entry = next((e for e in quarterly if e.metric.strip().lower() == margin_metric.lower()), None)
        if margin_entry:
            margin_values = [margin_entry.yoy_growth_pct, margin_entry.qoq_growth_pct]
            margin_values = [v for v in margin_values if v is not None]

    return ChartSeries(labels=labels, values=values, margin_or_growth=margin_values)


def render_chart(series: ChartSeries, title: str, filename: str) -> str:
    """
    Renders a bar (absolute value) + line (margin/growth %) combo chart,
    matching Geojit's chart style. Returns the saved file path.
    """
    os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(CHART_OUTPUT_DIR, filename)

    fig, ax1 = plt.subplots(figsize=(5, 3))

    ax1.bar(series.labels, series.values, color="#2ca089", label=title)
    ax1.set_ylabel(title)

    if series.margin_or_growth and len(series.margin_or_growth) == len(series.labels):
        ax2 = ax1.twinx()
        ax2.plot(series.labels, series.margin_or_growth, color="#e07b28", marker="o", label="Growth/Margin %")
        ax2.set_ylabel("Growth/Margin (%)")

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(file_path, dpi=120)
    plt.close(fig)

    return file_path


def generate_all_charts(quarterly: list[QuarterlyFinancialEntry]) -> Charts:
    """
    Builds and renders Revenue, EBITDA, and PAT charts from quarterly data.
    Gross Order Value is skipped by default since it's not part of the
    standard schema fields extracted (only present for specific sectors like
    Eternal/Zomato) — extend SECTION_KEYWORDS/quarterly prompt if needed.
    """
    charts = Charts()

    revenue_series = build_chart_series(quarterly, "Sales")
    if revenue_series:
        charts.revenue = revenue_series
        charts.revenue_chart_path = render_chart(revenue_series, "Revenue", "revenue.png")

    ebitda_series = build_chart_series(quarterly, "EBITDA", margin_metric="Margin (%)")
    if ebitda_series:
        charts.ebitda = ebitda_series
        charts.ebitda_chart_path = render_chart(ebitda_series, "EBITDA", "ebitda.png")

    pat_series = build_chart_series(quarterly, "Adj PAT")
    if pat_series:
        charts.pat = pat_series
        charts.pat_chart_path = render_chart(pat_series, "PAT", "pat.png")

    return charts