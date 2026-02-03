# Business Analytics & Reporting Directives

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-01-27
**Keywords:** Business intelligence, dashboards, KPIs, reporting, visualization, stakeholder reports, metrics, Snowsight, executive dashboards, data storytelling, WCAG accessibility
**TokenBudget:** ~2750
**ContextTier:** High
**Depends:** 000-global-core.md, 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Comprehensive directives for creating business-oriented queries, reports, dashboards, and visualizations targeted at non-technical stakeholders. Emphasizes clarity, actionable insights, ethical presentation, accessibility (WCAG 2.1 AA), and Snowflake-native dashboard capabilities.

**When to Load This Rule:**
- Creating business intelligence dashboards for stakeholders
- Building executive reports and KPI visualizations
- Designing Snowsight dashboards or Streamlit apps for business users
- Ensuring accessibility compliance (WCAG 2.1 AA)
- Implementing data storytelling and narrative-driven reports

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules
- **100-snowflake-core.md** - Snowflake SQL patterns

**Related:**
- **101-snowflake-streamlit-core.md** - Streamlit dashboard patterns
- **920-data-science-analytics.md** - Analytics and visualization patterns
- **132-snowflake-demo-modeling.md** - Data modeling and naming conventions

### External Documentation

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Snowsight Dashboards](https://docs.snowflake.com/en/user-guide/ui-snowsight-dashboards)

## Contract

### Inputs and Prerequisites

- Snowflake connection with read access to business-facing views/tables
- Understanding of target audience (C-Level, Directors, Analysts, Operations)
- Business context: KPIs, goals, decision-making needs
- Accessibility requirements (WCAG 2.1 AA compliance)

### Mandatory

- Snowflake SQL (CTEs, window functions, explicit columns)
- Snowsight Dashboards or Streamlit for visualization
- Business-friendly naming conventions
- Data quality indicators and freshness timestamps

### Forbidden

- Technical jargon without business translation
- SELECT * in production queries
- Misleading visualizations (truncated axes, 3D effects, dual Y-axes without marking)
- Non-accessible colors (red/green only, insufficient contrast)
- Undocumented metrics or calculations

### Execution Steps

1. Understand audience: Identify stakeholder role and information needs
2. Investigate data: Verify actual table schemas, data volumes, freshness
3. Define metrics: Document calculation logic, owners, update frequency
4. Optimize queries: Use CTEs, explicit columns, proper aggregation
5. Choose layout: F-pattern (dashboard) or Z-pattern (storytelling)
6. Select charts: Match visualization to data type and business question
7. Ensure accessibility: Test color contrast (4.5:1), screen reader, keyboard nav
8. Validate ethics: No misleading truncations, cherry-picking, or distortions
9. Add context: Include data freshness, filters, quality indicators

### Output Format

- SQL queries with business-friendly column names
- Dashboards with 5-7 visualizations max, <2s load time
- KPIs prominently displayed (top-left, above the fold)
- Data storytelling structure: Situation, Complication, Resolution, Evidence

### Validation

**Success Criteria:**
- Query execution <5s (verified in Query Profile)
- Dashboard loads <2s
- Color contrast ratio ≥4.5:1 (WebAIM verified)
- Screen reader narrates all content
- Business stakeholder confirms insights are actionable
- All metrics documented with definitions

### Design Principles

- **Business-First Language:** Translate technical outputs into business insights
- **Actionable Insights:** Every visualization should support a decision
- **Visual Hierarchy:** Most important information prominently placed (top-left)
- **Audience Segmentation:** Tailor complexity to role (C-Level vs Analyst)
- **Data Storytelling:** Structure reports as narratives with clear takeaways
- **Ethical Presentation:** No misleading manipulations; transparent about limitations
- **Accessibility:** Universal design for all users including colorblind, screen readers

### Post-Execution Checklist

- [ ] Business terminology used (no untranslated technical jargon)
- [ ] All KPIs clearly defined and documented
- [ ] WCAG 2.1 AA compliant (color contrast ≥4.5:1)
- [ ] F-pattern (execs) or Z-pattern (analysts) layout applied
- [ ] Data freshness indicator visible
- [ ] Explicit column selection (no SELECT *)
- [ ] Query execution <5s (Query Profile verified)
- [ ] Dashboard loads <2s
- [ ] Screen reader tested (NVDA/JAWS)
- [ ] Keyboard navigation works

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Cluttered Dashboard

```python
# BAD: 15 charts on one page - cognitive overload
st.plotly_chart(chart1); st.plotly_chart(chart2)  # ... 13 more
```

**Problem:** Information overload, unclear priorities, slow loading.

**Correct Pattern:**
```python
# GOOD: 5-7 focused visualizations with tabs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", "$12.5M", "+8%")
st.plotly_chart(primary_trend_chart)
tab1, tab2 = st.tabs(["Regional", "Product"])  # Details hidden
```

### Anti-Pattern 2: Technical Jargon Without Translation

```sql
-- BAD
SELECT cust_id, arpu, ltv_cac_ratio, churn_pct_30d FROM metrics;
```

**Problem:** Business stakeholders don't understand abbreviations.

**Correct Pattern:**
```sql
SELECT customer_id AS "Customer ID",
       average_revenue_per_user AS "Avg Revenue per Customer",
       thirty_day_churn_rate AS "30-Day Churn Rate (%)" FROM metrics;
```

### Anti-Pattern 3: Pie Chart with 12 Slices

```python
# BAD: Too many slices
fig = go.Figure(go.Pie(labels=all_12_categories, values=sales))
```

**Problem:** Impossible to compare similar-sized slices, cluttered legend.

**Correct Pattern:**
```python
# GOOD: Top 5 + "Other"
top_5 = df.nlargest(5, 'sales')
other_sum = df.nsmallest(len(df)-5, 'sales')['sales'].sum()
fig = go.Figure(go.Pie(labels=['A','B','C','D','E','Other'], values=[...], hole=0.3))
```

### Anti-Pattern 4: Misleading Truncated Y-Axis

```python
# BAD: Axis starts at 950, exaggerates small changes
fig.update_yaxis(range=[950, 1000])  # 1% looks like 100%!
```

**Problem:** Visually exaggerates small changes, misleads stakeholders.

**Correct Pattern:**
```python
fig.update_yaxis(range=[0, 1100])  # Zero baseline
fig.add_annotation(text="Sales grew 1% ($10 increase)")
```

### Anti-Pattern 5: Red/Green Color Scheme Only

```python
# BAD: 8% of males are red-green colorblind
fig.add_trace(go.Bar(name='Profit', marker_color='green'))
fig.add_trace(go.Bar(name='Loss', marker_color='red'))
```

**Problem:** Information inaccessible to colorblind users, WCAG failure.

**Correct Pattern:**
```python
# GOOD: Color + icons + patterns
fig.add_trace(go.Bar(name='Profit ▲', marker=dict(color='#029E73', pattern_shape="/")))
fig.add_trace(go.Bar(name='Loss ▼', marker=dict(color='#CC3311', pattern_shape="\\")))
```

## Audience Segmentation

**C-Level:** 4 KPIs, aggregated to company level, weekly update, trend lines
**Directors/VPs:** 5-8 KPIs, by department/region, daily update, comparison bars
**Analysts:** 10-15 KPIs, transaction-level access, real-time, scatter plots, pivot tables
**Operations:** 5-7 KPIs, real-time status/alerts, gauges, ranked lists

## Dashboard Layout Standards

### F-Pattern Layout (Standard Dashboard)

1. **Header Row:** Title, Last Update timestamp
2. **KPI Row:** 4-7 metrics prominently displayed
3. **Primary Chart Row:** Main insight visualization
4. **Supporting Charts:** 2-3 detail charts
5. **Detail Row:** Drill-down data table

**Rules:** Above-the-fold: KPIs + 1 primary chart; F-pattern scanning (top-left = highest priority); 30-40% white space.

### Z-Pattern Layout (Storytelling/Report)

1. **Executive Summary:** Key takeaway
2. **Primary Visual:** Evidence chart
3. **Supporting Analysis:** Detail charts

**Structure:** Situation, Complication, Resolution, Evidence

## Visualization Selection Matrix

**Comparison (Categories):** Horizontal bar (3-15 categories)
**Trend Analysis:** Line chart, Area chart (time series)
**Part-to-Whole:** Pie (2-5 slices), Donut, Stacked bar
**Distribution:** Histogram, Box plot, Violin plot
**Relationship:** Scatter plot, Bubble chart
**Ranking:** Horizontal bar (sorted), Lollipop
**Variance:** Waterfall chart, Bullet chart
**Geospatial:** Choropleth, Heat map, Point map
**Flow:** Sankey diagram, Funnel chart

**FORBIDDEN:** 3D pie charts, pie >5 slices, dual Y-axes with different scales, area charts for overlapping data

## Ethical Visualization Standards

**FORBIDDEN Manipulations:**
- Truncated Y-axis without clear visual indicators
- Cherry-picked date ranges without disclosure
- 3D effects that distort proportions
- Inconsistent time intervals

**Required Disclosures:**
```python
st.caption(f" Data as of: {last_update} ({hours_ago:.1f}h ago)")  # Freshness
st.info(f"Based on {len(df):,} responses | ±{margin:.1%} at 95% CI")  # Confidence
if active_filters: st.warning(f"Filters: {', '.join(active_filters)}")  # Filters
```

## Accessibility (WCAG 2.1 AA)

**Color Contrast:** Text 4.5:1, UI components 3:1 minimum

**Colorblind-Safe Palette:**
```python
COLORBLIND_SAFE = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC', '#CA9161', '#ECE133']
```

**Screen Reader Support:** Add alt text to charts, provide data table alternatives

**Keyboard Navigation:** Tab, Enter/Space, Arrow keys must work for all interactive elements

## Data Storytelling Framework

**Narrative Structure:**
1. **Situation:** Current state summary (2-3 sentences)
2. **Complication:** Problem or opportunity (annotated chart)
3. **Resolution:** Recommended action (highlighted text)
4. **Evidence:** Supporting visualizations

```python
st.header("Q3 2024 Performance")
st.write("**Situation:** Target was $15M revenue...")
st.write("**Finding:** Achieved $17.2M (+15%), driven by APAC 45% growth...")
st.success("**Recommendation:** Increase APAC sales team by 30%")
```

## Snowflake-Native Patterns

**Cost-Effective Queries:**
```sql
SELECT region, DATE_TRUNC('month', order_date) AS month,
       SUM(sales_amount) AS total_sales,
       APPROX_COUNT_DISTINCT(customer_id) AS unique_customers
FROM sales_fact WHERE order_date >= DATEADD('year', -2, CURRENT_DATE())
GROUP BY 1, 2;
```

**Streamlit Caching:**
```python
@st.cache_data(ttl=3600)  # 1 hour TTL
def load_dashboard_data(region: str):
    return session.sql(f"SELECT * FROM dashboard WHERE region = '{region}'").to_pandas()
```

## Metric Documentation Standard

```python
METRIC_DEFINITIONS = {
    "mrr": {
        "display_name": "Monthly Recurring Revenue (MRR)",
        "definition": "Sum of all active subscription values at month end",
        "calculation": "SUM(subscription_amount) WHERE status = 'active'",
        "owner": "Finance Team",
        "update_frequency": "Daily at 00:00 UTC"
    }
}
```
