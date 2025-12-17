# Business Analytics & Reporting Directives

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Business intelligence, dashboards, KPIs, reporting, visualization, stakeholder reports, metrics, Snowsight, executive dashboards, data storytelling, WCAG accessibility
**TokenBudget:** ~6400
**ContextTier:** High
**Depends:** None

## Purpose
Provide comprehensive directives for creating business-oriented queries, reports, dashboards, and visualizations targeted at non-technical stakeholders, emphasizing clarity, actionable insights, ethical presentation, accessibility, effective data storytelling, and Snowflake-native dashboard capabilities.

## Rule Scope
Business-oriented queries, reports, visualizations, and dashboards for business audience consumption across executive, director, analyst, and operational roles

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Business language first** - Use terminology stakeholders understand
- **Clear KPI definitions** - Document every metric calculation
- **WCAG AA accessibility** - Color contrast, screen readers, keyboard nav
- **F-pattern layout** - Key insights top-left for executive dashboards
- **Show data freshness** - Display "Last updated" prominently
- **Explicit columns** - Never SELECT * in production queries
- **Never mislead** - No truncated axes, 3D effects, or ambiguous charts

**Quick Checklist:**
- [ ] Business terminology used
- [ ] KPIs clearly defined
- [ ] WCAG 2.1 AA compliant
- [ ] F-pattern layout (execs) or Z-pattern (analysts)
- [ ] Data freshness indicator
- [ ] Explicit column selection
- [ ] Charts tested for clarity

## Contract

<contract>
<inputs_prereqs>
- Snowflake connection with read access to business-facing views/tables
- Understanding of target audience (C-Level, Directors, Analysts, Operations)
- Snowsight access for native dashboards or Streamlit for interactive apps
- Business context: KPIs, goals, decision-making needs
- Data freshness requirements and update schedules
- Accessibility requirements (WCAG 2.1 AA compliance)
</inputs_prereqs>

<mandatory>
- Snowflake SQL (CTEs, window functions, explicit columns)
- Snowsight Dashboards or Streamlit for visualization
- Query Profile for performance validation
- Accessibility testing tools (WebAIM contrast checker, screen readers)
- Business-friendly naming conventions
- Data quality indicators and freshness timestamps
</mandatory>

<forbidden>
- Technical jargon without business translation
- SELECT * in production queries (use explicit columns)
- Misleading visualizations (truncated axes, 3D effects, dual Y-axes without clear marking)
- Non-accessible colors (red/green only, insufficient contrast)
- Undocumented metrics or calculations
- Unqualified object names (always use DATABASE.SCHEMA.TABLE)
</forbidden>

<steps>
1. **Understand audience:** Identify stakeholder role and information needs
2. **Investigate data:** Verify actual table schemas, data volumes, freshness
3. **Define metrics:** Document calculation logic, owners, update frequency
4. **Optimize queries:** Use CTEs, explicit columns, proper aggregation
5. **Choose layout:** Select F-pattern (dashboard) or Z-pattern (storytelling)
6. **Select charts:** Match visualization to data type and business question
7. **Ensure accessibility:** Test color contrast (4.5:1), screen reader, keyboard nav
8. **Validate ethics:** No misleading truncations, cherry-picking, or distortions
9. **Add context:** Include data freshness, filters, quality indicators
10. **Test with users:** Validate dashboard meets business needs
</steps>

<output_format>
- SQL queries with business-friendly column names, proper comments
- Dashboards with 5-7 visualizations max, clear hierarchy, <2s load time
- KPIs prominently displayed (top-left to top-right, above the fold)
- Visualizations with clear titles, labeled axes, legends, annotations
- Data storytelling structure: Situation, then Complication, then Resolution, then Evidence
- Accessibility: WCAG 2.1 AA compliant, screen reader tested, keyboard accessible
</output_format>

<validation>
1. Query execution <5s (test in Query Profile)
2. Dashboard loads <2s (test with production data)
3. Color contrast ratio ≥4.5:1 (test with WebAIM contrast checker)
4. Screen reader narrates all content (test with NVDA/JAWS)
5. Keyboard navigation works (Tab, Enter, Arrow keys)
6. Business stakeholder confirms insights are actionable
7. All metrics documented with definitions
8. Data freshness indicator visible and accurate
</validation>

<design_principles>
- **Business-First Language:** Translate technical outputs into business insights
- **Actionable Insights:** Every visualization should support a decision
- **Visual Hierarchy:** Most important information prominently placed (top-left)
- **Audience Segmentation:** Tailor complexity and detail to role (C-Level vs Analyst)
- **Data Storytelling:** Structure reports as narratives with clear takeaways
- **Ethical Presentation:** No misleading manipulations; transparent about limitations
- **Accessibility:** Universal design for all users including colorblind, screen readers
- **Performance:** Optimize for fast loading and responsive interaction
- **Snowflake-Native:** Leverage Snowsight, Streamlit, cost-effective SQL patterns
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Cluttered Dashboard (Too Many Visualizations)**
```python
# BAD: 15 charts on one page
st.plotly_chart(chart1)
st.plotly_chart(chart2)
# ... 13 more charts
# Result: Information overload, slow loading, confused users
```
**Problem:**
- Cognitive overload for users
- Unclear what's most important
- Slow dashboard load times

**Correct Pattern:**
```python
# GOOD: 5-7 focused visualizations with tabs for details
# Main page: Executive summary
col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", "$12.5M", "+8%")
col2.metric("Customers", "15,234", "+12%")
col3.metric("Retention", "94%", "-2%")
col4.metric("NPS", "72", "+5")

st.plotly_chart(primary_trend_chart)

# Details in tabs
tab1, tab2, tab3 = st.tabs(["Regional", "Product", "Customer"])
with tab1:
 st.plotly_chart(regional_analysis)
```
**Benefits:**
- Clear visual hierarchy
- Fast initial load
- Progressive disclosure for details


**Anti-Pattern 2: Technical Jargon Without Business Translation**
```sql
-- BAD: Technical column names
SELECT
 cust_id,
 arpu,
 ltv_cac_ratio,
 churn_pct_30d
FROM metrics;
```
**Problem:**
- Business stakeholders don't understand abbreviations
- Requires constant translation
- Reduces dashboard adoption

**Correct Pattern:**
```sql
-- GOOD: Business-friendly column names
SELECT
 customer_id AS "Customer ID",
 average_revenue_per_user AS "Avg Revenue per Customer",
 lifetime_value_to_acquisition_cost_ratio AS "LTV:CAC Ratio",
 thirty_day_churn_rate AS "30-Day Churn Rate (%)"
FROM metrics;
```
**Benefits:**
- Self-explanatory to business users
- No translation needed
- Higher dashboard adoption


**Anti-Pattern 3: Pie Chart with 12 Slices**
```python
# BAD: Too many slices to distinguish
fig = go.Figure(go.Pie(
 labels=all_12_product_categories,
 values=sales_by_category
))
```
**Problem:**
- Impossible to compare similar-sized slices
- Legend becomes cluttered
- Colors hard to distinguish

**Correct Pattern:**
```python
# GOOD: Show top 5, group rest as "Other"
top_5 = df.nlargest(5, 'sales')
other_sum = df.nsmallest(len(df)-5, 'sales')['sales'].sum()

chart_data = pd.concat([
 top_5,
 pd.DataFrame({'category': ['Other'], 'sales': [other_sum]})
])

fig = go.Figure(go.Pie(
 labels=chart_data['category'],
 values=chart_data['sales'],
 hole=0.3 # Donut chart easier to read
))
```
**Benefits:**
- Clear comparison of top categories
- "Other" provides context without clutter
- Easy to interpret at a glance


**Anti-Pattern 4: Misleading Truncated Y-Axis**
```python
# BAD: Axis starts at 950, makes small change look huge
fig = go.Figure(go.Line(x=months, y=[980, 985, 990]))
fig.update_yaxis(range=[950, 1000])
# 1% change looks like 100% change!
```
**Problem:**
- Visually exaggerates small changes
- Misleads stakeholders
- Damages trust

**Correct Pattern:**
```python
# GOOD: Include zero baseline or clearly mark truncation
fig = go.Figure(go.Line(x=months, y=[980, 985, 990]))
fig.update_yaxis(range=[0, 1100]) # Zero baseline
fig.add_annotation(
 text="Sales grew 1% ($10 increase)",
 xref="paper", yref="paper",
 x=0.5, y=1.1
)
```
**Benefits:**
- Honest visual representation
- Maintains stakeholder trust
- Accurate perception of change magnitude


**Anti-Pattern 5: Red/Green Color Scheme Only**
```python
# BAD: Colorblind users can't distinguish
fig = go.Figure()
fig.add_trace(go.Bar(name='Profit', marker_color='green'))
fig.add_trace(go.Bar(name='Loss', marker_color='red'))
# 8% of males can't tell these apart!
```
**Problem:**
- Red-green colorblindness affects 8% of males
- Information inaccessible to significant user segment
- WCAG compliance failure

**Correct Pattern:**
```python
# GOOD: Color + shape + pattern
fig = go.Figure()
fig.add_trace(go.Bar(
 name='Profit ▲',
 marker=dict(
 color='#029E73', # Colorblind-safe green
 pattern_shape="/"
 )
))
fig.add_trace(go.Bar(
 name='Loss ▼',
 marker=dict(
 color='#CC3311', # Colorblind-safe red
 pattern_shape="\\"
 )
))
```
**Benefits:**
- Accessible to colorblind users
- Multiple encoding channels (color + icon + pattern)
- WCAG 2.1 AA compliant

> **Investigation Required**
> When applying this rule:
>
> 1. **Read referenced tables/views BEFORE making recommendations**
> - Check actual schemas: `DESCRIBE TABLE table_name`
> - Verify row counts: `SELECT COUNT(*) FROM table_name`
> - Sample data to understand business context
>
> 2. **Verify business assumptions against actual data**
> - Don't assume metric definitions (check with stakeholders or documentation)
> - Don't guess at data granularity (check actual records)
> - Don't speculate about update frequency (verify with last_modified timestamps)
>
> 3. **Never speculate about business requirements**
> - Ask: "What decision will this dashboard support?"
> - Ask: "Who is the primary audience?"
> - Ask: "What action should users take based on this data?"
>
> 4. **If uncertain about audience needs, explicitly state:**
> - "Let me confirm the target audience before designing the layout."
> - "I need to understand the key business questions this dashboard answers."
> - "Let me verify the metric definitions with the business owner."
>
> 5. **Make grounded, business-focused recommendations**
> - Base dashboard design on actual audience role and needs
> - Reference specific business metrics from investigation
> - Provide examples using actual column names from schemas
>
> **Example Investigation Pattern:**
> ```python
> # GOOD: Investigate business context first
> tables = session.sql("SHOW TABLES IN SCHEMA analytics").collect()
> schema = session.sql("DESCRIBE TABLE analytics.sales_summary").collect()
> sample = session.sql("SELECT * FROM analytics.sales_summary LIMIT 10").to_pandas()
>
> # Check data freshness
> last_update = session.sql("""
> SELECT MAX(last_updated)
> FROM analytics.sales_summary
> """).collect()[0][0]
>
> # Now make informed recommendations
> st.info(f" Data updated {last_update}. Recommend hourly refresh for operational dashboard.")
> ```

## Post-Execution Checklist

- [ ] Audience role identified and dashboard tailored accordingly
- [ ] Data investigation completed (schemas, volumes, freshness verified)
- [ ] 4-7 KPIs displayed prominently above the fold
- [ ] 5-7 visualizations maximum per page (use tabs for more)
- [ ] Chart types appropriate for data purpose (decision matrix followed)
- [ ] Ethical standards met (no misleading truncations, cherry-picking, 3D effects)
- [ ] Color contrast tested (≥4.5:1 ratio for text)
- [ ] Colorblind-safe palette used (not red/green only)
- [ ] Screen reader tested (alt text, data table alternative provided)
- [ ] Keyboard navigation verified (Tab, Enter, Arrow keys work)
- [ ] Data freshness indicator visible
- [ ] Active filters/exclusions disclosed
- [ ] All metrics documented with definitions
- [ ] SQL queries optimized (Query Profile shows <5s, <$0.10)
- [ ] Storytelling structure followed (Situation-Complication-Resolution)
- [ ] Business language used (no unexplained technical jargon)

## Validation

- **Success Checks:**
 - Dashboard loads in <2 seconds with production data
 - Business stakeholder confirms insights are actionable
 - Query Profile shows <5s execution, <$0.10 cost per query
 - WCAG 2.1 AA color contrast test passes (WebAIM checker)
 - Screen reader successfully narrates all content (NVDA/JAWS test)
 - Keyboard navigation works for all interactive elements

> **Investigation Required**
> When applying this rule:
> 1. **Identify audience BEFORE designing dashboard** - Confirm exec vs analyst vs operational
> 2. **Check data availability** - Verify tables/views exist and are accessible
> 3. **Never assume KPI definitions** - Confirm metric calculations with stakeholders
> 4. **Test accessibility** - Use screen readers and color contrast checkers
> 5. **Verify query cost** - Review Query Profile before deploying
>
> **Anti-Pattern:**
> "Creating dashboard... (without knowing target audience)"
> "Using red/green colors... (without colorblind testing)"
>
> **Correct Pattern:**
> "Let me confirm your dashboard requirements first."
> [identifies audience, checks data, verifies KPI definitions]
> "I see this is for C-Level. Using F-pattern with 5 KPIs and colorblind-safe palette..."
 - User testing shows >90% task completion rate
 - All metrics have documented definitions in METRIC_DEFINITIONS

- **Negative Tests:**
 - Dashboard with >10 visualizations (should simplify with tabs/drill-downs)
 - Chart with truncated Y-axis without annotation (should fail ethics review)
 - Red/green only color scheme (should fail colorblind accessibility test)
 - Text with <4.5:1 contrast ratio (should fail WCAG compliance)
 - Query taking >10 seconds (should optimize with Query Profile)
 - Metric without documented definition (should fail documentation requirement)
 - Technical jargon without business translation (should fail user comprehension test)

## Output Format Examples

```sql
-- Business Analytics Query Template
-- Filename: monthly_sales_analysis.sql
-- Description: Monthly sales trends by region for executive dashboard

-- Always use CTEs for clarity
WITH base_sales AS (
 SELECT
 DATE_TRUNC('month', order_date) AS month,
 region,
 customer_id,
 sales_amount
 FROM PROD_DB.SALES.ORDERS
 WHERE order_date >= DATEADD('year', -2, CURRENT_DATE())
 AND status = 'completed'
),

aggregated AS (
 SELECT
 month,
 region,
 SUM(sales_amount) AS "Total Sales",
 APPROX_COUNT_DISTINCT(customer_id) AS "Unique Customers",
 SUM(sales_amount) / NULLIF(APPROX_COUNT_DISTINCT(customer_id), 0) AS "Avg Revenue per Customer"
 FROM base_sales
 GROUP BY 1, 2
)

SELECT * FROM aggregated
ORDER BY month DESC, "Total Sales" DESC;

-- Visualization: Line chart (time series trend)
-- Audience: C-Level executives
-- Update Frequency: Daily
```

```python
# Streamlit Dashboard Template
import streamlit as st
import plotly.graph_objects as go
from snowflake.snowpark import Session

# Page config
st.set_page_config(
 page_title="Sales Executive Dashboard",
 page_icon="",
 layout="wide"
)

# Data freshness indicator
st.caption(f" Data as of: {last_update} | Updated: {hours_ago:.1f}h ago")

# KPIs (above the fold)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", "$12.5M", delta="+8.2%")
col2.metric("Customers", "15,234", delta="+12%")
col3.metric("Retention", "94%", delta="-2%", delta_color="inverse")
col4.metric("NPS Score", "72", delta="+5")

# Primary visualization
fig = go.Figure(go.Scatter(
 x=df['month'],
 y=df['revenue'],
 mode='lines+markers',
 line=dict(color='#0173B2', width=3),
 marker=dict(size=8)
))
fig.update_layout(
 title="Monthly Revenue Trend",
 xaxis_title="Month",
 yaxis_title="Revenue ($ Millions)",
 yaxis=dict(range=[0, df['revenue'].max() * 1.1]) # Zero baseline
)
st.plotly_chart(fig, use_container_width=True)

# Supporting details in expander
with st.expander(" View Detailed Breakdown"):
 st.dataframe(df, use_container_width=True)

# Metric definitions
with st.expander("ℹ️ Metric Definitions"):
 st.write("**Revenue:** Total value of completed orders (excludes refunds and cancellations)")
 st.write("**Customers:** Count of unique customer IDs with at least one completed order")
```

## References

### External Documentation
- [Business Intelligence Best Practices](https://docs.microsoft.com/en-us/power-bi/guidance/) - Microsoft Power BI guidance for business analytics
- [Data Visualization Principles](https://www.tableau.com/learn/articles/data-visualization) - Tableau's guide to effective data visualization
- [SQL for Business Analysis](https://mode.com/sql-tutorial/) - Comprehensive SQL tutorial focused on business analytics
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Web Content Accessibility Guidelines
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) - Tool for testing color contrast ratios
- [Colorblind-Safe Palettes](https://davidmathlogic.com/colorblind/) - Research-based colorblind-friendly color schemes
- [Snowsight Dashboard Documentation](https://docs.snowflake.com/en/user-guide/ui-snowsight-dashboards) - Snowflake native dashboards
- [Streamlit Documentation](https://docs.streamlit.io/) - Interactive dashboard development

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Snowflake SQL Demo Engineering**: `rules/102-snowflake-sql-demo-engineering.md`
- **Snowflake Performance Tuning**: `rules/103-snowflake-performance-tuning.md`
- **Snowflake Cost Governance**: `rules/105-snowflake-cost-governance.md`
- **Snowflake Streamlit UI**: `rules/101-snowflake-streamlit-core.md`
- **Snowflake Data Quality**: `rules/124-snowflake-data-quality-core.md`
- **Data Science Analytics**: `rules/920-data-science-analytics.md`
- **Data Governance**: `rules/930-data-governance-quality.md`

> ** Claude 4 Specific Guidance**
> **Claude 4 Optimizations:**
> - **Context awareness:** Track token budget; prioritize audience segmentation and ethical standards sections
> - **Explicit behavior:** Request "comprehensive dashboard with accessibility compliance" to get full implementation
> - **Parallel tool calls:** Generate multiple chart types, validate SQL queries, check accessibility simultaneously
> - **State discovery:** Leverage filesystem to check existing dashboard templates before creating new ones
> - **Investigation-first:** Excel at business context discovery through data exploration - use this capability to understand stakeholder needs before designing dashboards

## 1. Audience Segmentation & Tailoring

**MANDATORY:**

### Dashboard Design by Audience

**C-Level (CEO, CFO, COO):**
- KPI Count: 3-5, Detail: High-level trends/variance to goals
- Update: Daily/Weekly, Charts: Trend lines, variance bars, bullet charts
- Interaction: Minimal filters, drill to summary

**Directors/VPs:**
- KPI Count: 5-8, Detail: Aggregated by department/region
- Update: Daily, Charts: Comparison bars, heat maps, waterfall charts
- Interaction: Department filters, time periods

**Analysts:**
- KPI Count: 10-15, Detail: Granular, transaction-level access
- Update: Real-time/Hourly, Charts: Scatter plots, distributions, pivot tables
- Interaction: Heavy filtering, drill-down, export

**Operations:**
- KPI Count: 5-7, Detail: Real-time status, alerts
- Update: Hourly/Real-time, Charts: Gauges, status indicators, ranked lists
- Interaction: Action buttons, alert thresholds

**Example Implementation:**
```python
# Streamlit: Adapt dashboard to user role
import streamlit as st

user_role = st.session_state.get('user_role', 'analyst')

if user_role == 'executive':
 # C-Level: 4 KPIs, 2 trend charts
 col1, col2, col3, col4 = st.columns(4)
 col1.metric("Revenue", "$12.5M", delta="+8.2%")
 col2.metric("Profit Margin", "23.1%", delta="+1.5%")
 col3.metric("Customer Retention", "94.2%", delta="-0.8%", delta_color="inverse")
 col4.metric("NPS Score", "72", delta="+5")

 # Single high-level trend
 st.line_chart(monthly_revenue_trend)

elif user_role == 'analyst':
 # Analyst: 12 KPIs, 8 detail charts, heavy filtering
 with st.sidebar:
 date_range = st.date_input("Date Range", [start_date, end_date])
 region = st.multiselect("Region", all_regions)
 product = st.multiselect("Product", all_products)

 # Show detailed breakdowns
 st.dataframe(detailed_data, use_container_width=True)
```

## 2. Dashboard Layout & Visual Hierarchy

**MANDATORY:**

### F-Pattern Layout (Standard Dashboard)

**Dashboard Layout Structure:**

1. **Header Row:** Dashboard Title, Last Update timestamp
2. **KPI Row (Top priority metrics):**
   - KPI 1: $12.5M (+8.2% up)
   - KPI 2: 23.1% (+1.5% up)
   - KPI 3: 94.2% (-0.8% down)
   - KPI 4: 72 (+5 up)
3. **Primary Chart Row (Main insight):** Revenue Trend
4. **Supporting Charts Row (Supporting details):**
   - Chart 2: Regional Performance
   - Chart 3: Product Mix
5. **Detail Row (Drill-down data):** Detailed Table: Top 10 Customers

**Layout Rules:**
- **Above the fold:** 4-7 KPIs + 1 primary chart
- **F-Pattern scanning:** Top-left = highest priority
- **White space:** 30-40% empty for breathing room
- **Grid alignment:** Snap to 12-column grid for consistency

### Z-Pattern Layout (Storytelling/Report)

**Narrative Dashboard Flow:**

1. **Executive Summary (Key takeaway):**
   - "Revenue grew 8% driven by new customer acquisition in APAC region"
2. **Primary Visual (Visual evidence):**
   - Chart 1: Revenue Trend with APAC Highlight
3. **Supporting Analysis (Details):**
   - Chart 2, Chart 3

**Storytelling Structure:**
1. **Situation:** Current state summary (text box, 2-3 sentences)
2. **Complication:** Problem or opportunity identified (annotated chart)
3. **Resolution:** Recommended action or insight (highlighted text)
4. **Evidence:** Supporting data visualizations

### Information Density Guidelines

**MANDATORY:**

- **5-7 visualizations maximum** per dashboard page
- **4-7 KPIs** prominently displayed (more dilutes focus)
- **30-40% white space** for visual breathing room
- **Progressive disclosure:** Use tabs, accordions, drill-downs rather than cramming everything
- **Mobile-first:** Design for smallest screen first, enhance for desktop

**Example: Progressive Disclosure**
```python
# Streamlit: Use tabs for complexity
tab1, tab2, tab3 = st.tabs(["Overview", "Regional Detail", "Product Analysis"])

with tab1:
 # Overview: 4 KPIs + 1 trend
 show_high_level_summary()

with tab2:
 # Detail: Regional breakdowns (hidden by default)
 show_regional_analysis()

with tab3:
 # Deep dive: Product-level data
 show_product_analysis()
```

## 3. Visualization Selection Framework

**MANDATORY:**

### Comprehensive Chart Type Decision Matrix

**Chart Selection by Data Purpose:**

**Comparison (Categories):**
- Use: Horizontal bar chart for 3-15 categories
- Avoid: >15 categories (use sorted table instead)

**Trend Analysis:**
- Use: Line chart, Area chart for time series, continuous progression
- Avoid: <4 data points (use column chart instead)

**Part-to-Whole:**
- Use: Pie chart (2-5 slices), Donut chart, Stacked bar for simple proportions
- Avoid: >5 categories or when precise comparison needed

**Distribution:**
- Use: Histogram, Box plot, Violin plot for data spread, outliers, statistical analysis
- Avoid: Categorical data

**Relationship:**
- Use: Scatter plot, Bubble chart for correlation between 2-3 variables
- Avoid: When no clear relationship exists

**Ranking:**
- Use: Horizontal bar (sorted), Lollipop chart for ordered comparisons, league tables
- Avoid: Unordered categories

**Variance:**
- Use: Waterfall chart, Bullet chart for changes decomposition, actual vs target
- Avoid: Simple trends (use line instead)

**Volume:**
- Use: Bubble chart, Symbol map when 3rd dimension (size) needed
- Avoid: When size differences too subtle
| **Geospatial** | Choropleth map, Heat map, Point map | Location-based patterns | Data not tied to geography |
| **Hierarchical** | Tree map, Sunburst chart | Nested categories, drill-down | Flat relationships |
| **Flow** | Sankey diagram, Funnel chart | Process steps, conversion paths | No sequential relationship |

### Domain-Specific Visualization Patterns

**Financial Analytics:**
```sql
-- Waterfall chart for P&L decomposition
WITH pl_components AS (
 SELECT 'Revenue' AS component, 1 AS sort_order, 5000000 AS amount
 UNION ALL SELECT 'COGS', 2, -2000000
 UNION ALL SELECT 'Gross Profit', 3, 3000000
 UNION ALL SELECT 'OpEx', 4, -1500000
 UNION ALL SELECT 'EBITDA', 5, 1500000
 UNION ALL SELECT 'D&A', 6, -200000
 UNION ALL SELECT 'Net Income', 7, 1300000
)
SELECT * FROM pl_components ORDER BY sort_order;

-- Visualize in Streamlit with Plotly
import plotly.graph_objects as go

fig = go.Figure(go.Waterfall(
 x=df['component'],
 y=df['amount'],
 text=df['amount'].apply(lambda x: f'${x/1e6:.1f}M'),
 connector={"line": {"color": "rgb(63, 63, 63)"}},
))
fig.update_layout(title="P&L Waterfall Analysis")
st.plotly_chart(fig)
```

**Marketing Analytics:**
```sql
-- Funnel chart for conversion analysis
SELECT
 'Website Visits' AS stage, 1 AS sort_order, 100000 AS count
UNION ALL SELECT 'Product Views', 2, 45000
UNION ALL SELECT 'Add to Cart', 3, 15000
UNION ALL SELECT 'Checkout Started', 4, 8000
UNION ALL SELECT 'Purchase Complete', 5, 5000
ORDER BY sort_order;

-- Conversion rates at each stage
WITH funnel AS (
 -- above query
)
SELECT
 stage,
 count,
 LAG(count) OVER (ORDER BY sort_order) AS previous_stage_count,
 count / LAG(count) OVER (ORDER BY sort_order) AS conversion_rate
FROM funnel;
```

**Operational Analytics:**
```python
# Gauge charts for KPI performance vs target
import plotly.graph_objects as go

fig = go.Figure(go.Indicator(
 mode="gauge+number+delta",
 value=94.2,
 title={'text': "On-Time Delivery Rate"},
 delta={'reference': 95, 'valueformat': '.1f'},
 gauge={
 'axis': {'range': [None, 100]},
 'bar': {'color': "darkblue"},
 'steps': [
 {'range': [0, 80], 'color': "lightcoral"},
 {'range': [80, 95], 'color': "lightyellow"},
 {'range': [95, 100], 'color': "lightgreen"}
 ],
 'threshold': {'line': {'color': "red", 'width': 4}, 'value': 95}
 }
))
st.plotly_chart(fig)
```

### Chart Selection Anti-Patterns

**FORBIDDEN:**

**Never:**
- **3D pie charts** (distorts proportions)
- **Pie charts with >5 slices** (hard to compare)
- **Dual Y-axes with vastly different scales** (unless clearly marked and justified)
- **Area charts for overlapping data** (use line charts instead)
- **Radar charts for more than 5-7 dimensions** (cluttered and hard to interpret)

## 4. Ethical Visualization Standards

**FORBIDDEN:**

### Forbidden Manipulations

**Never truncate Y-axis without clear visual indicators:**
```python
# BAD: Misleading truncation
fig = go.Figure(go.Bar(x=['Q1', 'Q2', 'Q3'], y=[95000, 96000, 97000]))
fig.update_yaxis(range=[94000, 98000]) # Makes 3% look like 300%!

# GOOD: Include zero baseline or add break indicator
fig = go.Figure(go.Bar(x=['Q1', 'Q2', 'Q3'], y=[95000, 96000, 97000]))
fig.update_yaxis(range=[0, 100000])
fig.add_annotation(
 text="Revenue grew $2K (3%)",
 xref="paper", yref="paper",
 x=0.5, y=1.1, showarrow=False
)
```

**Never cherry-pick date ranges without disclosure:**
```sql
-- BAD: Showing only favorable period
SELECT * FROM sales
WHERE order_date BETWEEN '2024-03-01' AND '2024-03-31'; -- Best month only

-- GOOD: Show full context with annotation
SELECT
 DATE_TRUNC('month', order_date) AS month,
 SUM(sales_amount) AS total_sales
FROM sales
WHERE order_date >= DATEADD('year', -2, CURRENT_DATE())
GROUP BY 1
ORDER BY 1;

-- Add dashboard annotation: "March 2024 was exceptional due to product launch"
```

**Never use 3D effects that distort proportions:**
```python
# FORBIDDEN: 3D pie chart
# 3D perspective makes front slices appear larger

# CORRECT: 2D pie or donut chart with clear labels
fig = go.Figure(go.Pie(
 labels=['Product A', 'Product B', 'Product C'],
 values=[40, 35, 25],
 hole=0.3, # Donut chart
 textinfo='label+percent',
 textposition='outside'
))
```

### Required Disclosures

**MANDATORY:**

**Data Freshness:**
```python
# Every dashboard must show when data was last updated
from datetime import datetime

last_update = get_last_refresh_timestamp()
hours_ago = (datetime.now() - last_update).total_seconds() / 3600

st.caption(f" Data as of: {last_update.strftime('%Y-%m-%d %H:%M')} ({hours_ago:.1f}h ago)")
```

**Sample Size & Confidence:**
```python
# Show statistical confidence for surveys/samples
st.info(f"Based on {len(df):,} responses | Margin of error: ±{margin_of_error:.1%} at 95% confidence")
```

**Filters & Exclusions:**
```python
# Alert users when filters are active
active_filters = []
if region_filter != 'All':
 active_filters.append(f"Region: {region_filter}")
if date_range != default_range:
 active_filters.append(f"Date: {date_range}")

if active_filters:
 st.warning(f"Active filters: {', '.join(active_filters)}")
```

**Data Quality Warnings:**
```python
# Show data quality status
quality_score = calculate_quality_score(df)
if quality_score < 0.9:
 st.error(f"Data quality: {quality_score:.0%} | Review {issues_count} flagged records before making decisions")
elif quality_score < 0.95:
 st.warning(f"Data quality: {quality_score:.0%} | Some incomplete records present")
else:
 st.success(f"Data quality: {quality_score:.0%} | All checks passed")
```

## 5. Accessibility (WCAG 2.1 AA Compliance)

**MANDATORY:**

### Color Contrast Requirements

**Text Contrast:**
- **Large text (18pt+):** 3:1 minimum
- **Normal text:** 4.5:1 minimum
- **UI components:** 3:1 minimum

**Testing:** Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/

**Example Compliant Colors:**
```python
# WCAG AA compliant color palette
ACCESSIBLE_PALETTE = {
 'primary': '#0173B2', # Blue (contrast: 8.59:1 on white)
 'secondary': '#DE8F05', # Orange (contrast: 5.47:1)
 'success': '#029E73', # Green (contrast: 5.93:1)
 'warning': '#FBC02D', # Yellow (contrast: 12.63:1)
 'danger': '#CC3311', # Red (contrast: 5.95:1)
 'info': '#5E35B1', # Purple (contrast: 7.67:1)
}
```

### Colorblind-Safe Design

**MANDATORY:**

**Never rely on color alone for information:**
```python
# BAD: Red/green only (8% of males are red-green colorblind)
fig = go.Figure()
fig.add_trace(go.Bar(x=categories, y=profits, name='Profit', marker_color='green'))
fig.add_trace(go.Bar(x=categories, y=losses, name='Loss', marker_color='red'))

# GOOD: Color + icons + patterns
fig = go.Figure()
fig.add_trace(go.Bar(
 x=categories, y=profits,
 name='Profit ▲',
 marker=dict(color='#029E73', pattern_shape="/") # Green + pattern
))
fig.add_trace(go.Bar(
 x=categories, y=losses,
 name='Loss ▼',
 marker=dict(color='#CC3311', pattern_shape="\\") # Red + pattern
))
```

**Use colorblind-safe palettes:**
```python
# Paul Tol's colorblind-safe palette
COLORBLIND_SAFE = [
 '#0173B2', '#DE8F05', '#029E73', # Blue, Orange, Green
 '#CC78BC', '#CA9161', '#ECE133', # Purple, Brown, Yellow
 '#949494' # Gray
]

# For diverging data (e.g., sentiment)
DIVERGING_COLORBLIND = [
 '#364B9A', '#4A7BB7', '#6EA6CD', # Blues (negative)
 '#EAECCC', # Neutral
 '#FDB366', '#F67E4B', '#DD3D2D' # Oranges (positive)
]
```

### Screen Reader Support

**Add descriptive alt text to all charts:**
```python
fig.update_layout(
 title={
 'text': "Monthly Sales Trend",
 'subtitle': {
 'text': "Line chart showing sales from $1M in January to $3M in December 2024. Steady growth with spike in November due to Black Friday."
 }
 },
 xaxis_title="Month",
 yaxis_title="Sales ($ Millions)"
)
```

**Provide data table alternatives:**
```python
# Always offer data table for screen readers
with st.expander("View Data Table (Accessible Format)"):
 st.dataframe(
 df,
 use_container_width=True,
 hide_index=False
 )

 # Allow CSV download for external analysis
 csv = df.to_csv(index=False)
 st.download_button(
 label="Download CSV",
 data=csv,
 file_name="data.csv",
 mime="text/csv"
 )
```

### Keyboard Navigation

**MANDATORY:**

**Ensure all interactive elements are keyboard accessible:**
- Tab: Navigate between elements
- Enter/Space: Activate buttons/links
- Arrow keys: Navigate within lists/menus
- Esc: Close modals/dropdowns

**Test checklist:**
- [ ] All filters reachable via Tab key
- [ ] Buttons activate with Enter/Space
- [ ] Focus indicator clearly visible (2px outline minimum)
- [ ] Skip-to-content link available
- [ ] No keyboard traps (can always navigate away)

## 6. Data Storytelling Framework

**MANDATORY:**

### Narrative Structure: Situation-Complication-Resolution

**1. Situation (What's the current state?):**
```python
st.header("Q3 2024 Performance Summary")
st.write("""
**Situation:** We set a target of $15M revenue for Q3 2024, expecting 10% growth
over Q2 based on new product launches and expanded sales team.
""")
```

**2. Complication (What's the problem/opportunity?):**
```python
st.write("""
**Finding:** We achieved $17.2M revenue (+15% vs target), driven by unexpected
strength in APAC region which grew 45% while North America remained flat.
""")

# Visual evidence
fig = create_regional_performance_chart()
fig.add_annotation(
 x='APAC', y=apac_value,
 text='45% growth!',
 showarrow=True,
 arrowhead=2
)
st.plotly_chart(fig)
```

**3. Resolution (What action should be taken?):**
```python
st.success("""
**Recommendation:** Increase APAC sales team by 30% and reallocate 20% of
North America marketing budget to APAC digital campaigns for Q4.
""")
```

**4. Supporting Evidence (Detailed data):**
```python
with st.expander(" Detailed Regional Analysis"):
 st.dataframe(regional_breakdown)
 st.plotly_chart(detailed_trend_chart)
```

### Executive Summary Best Practices

**Top of every report/dashboard:**
```python
st.markdown("""
### Executive Summary

**Key Takeaways:**
1. **Revenue exceeded target by 15%** ($17.2M vs $15M goal)
2. **APAC region outperformed** with 45% growth
3. **North America growth stalled** at 2% (vs 10% target)
4. **Recommendation:** Shift resources to high-growth APAC market

*Scroll down for detailed analysis and supporting data.*
""")
```

## 7. Snowflake-Native Dashboard Patterns

**MANDATORY:**

### Snowsight Dashboards

**Cost-Effective Query Patterns:**
```sql
-- Use result caching for dashboards (queries <24h old cached free)
SELECT
 region,
 DATE_TRUNC('month', order_date) AS month,
 SUM(sales_amount) AS total_sales,
 APPROX_COUNT_DISTINCT(customer_id) AS unique_customers -- Faster than exact COUNT
FROM sales_fact
WHERE order_date >= DATEADD('year', -2, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY 1, 2;

-- Use explicit columns (not SELECT *)
-- Use APPROX_* functions for faster aggregation
-- Add WHERE filters to reduce data scanned
```

**Snowsight Chart Configuration:**
```yaml
# Bar chart for comparisons
chart_type: bar
orientation: horizontal # Easier to read category labels
sort: descending # Show highest values first
data_labels: on # Show values on bars
color_scheme: sequential_blue

# Line chart for trends
chart_type: line
x_axis: date_column
y_axis: metric_value
show_points: false # Cleaner for many data points
show_grid: true
```

### Streamlit with Snowflake Integration

**Optimized Data Loading:**
```python
import streamlit as st
from snowflake.snowpark import Session

# Initialize Snowpark session
session = Session.builder.configs(st.secrets["snowflake"]).create()

# Cache expensive queries (1 hour TTL)
@st.cache_data(ttl=3600)
def load_dashboard_data(region: str):
 return session.sql(f"""
 SELECT
 order_date,
 SUM(sales_amount) AS total_sales
 FROM sales_fact
 WHERE region = '{region}'
 AND order_date >= DATEADD('month', -12, CURRENT_DATE())
 GROUP BY 1
 ORDER BY 1
 """).to_pandas()

# Cache models/connections (persist across sessions)
@st.cache_resource
def get_session():
 return Session.builder.configs(st.secrets["snowflake"]).create()
```

### Performance Optimization

**Query Profile Validation:**
```python
# Always check Query Profile for dashboard queries
# Target: <5 seconds execution, <$0.10 cost

# Set query timeout
session.sql("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 30").collect()

# Monitor slow queries
slow_queries = session.sql("""
 SELECT
 query_text,
 execution_time,
 bytes_scanned,
 credits_used_cloud_services
 FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
 WHERE execution_status = 'SUCCESS'
 AND execution_time > 5000 -- >5 seconds
 AND start_time >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
 ORDER BY execution_time DESC
 LIMIT 10
""").to_pandas()

if not slow_queries.empty:
 st.warning(f"{len(slow_queries)} slow queries detected. Review Query Profile.")
```

## 8. Metric Definition & Documentation

**MANDATORY:**

### Metric Catalog Standard

```python
# Define all metrics in structured format
METRIC_DEFINITIONS = {
 "monthly_recurring_revenue": {
 "display_name": "Monthly Recurring Revenue (MRR)",
 "definition": "Sum of all active subscription values at month end",
 "calculation": """
 SELECT
 DATE_TRUNC('month', snapshot_date) AS month,
 SUM(subscription_amount) AS mrr
 FROM subscriptions
 WHERE status = 'active'
 GROUP BY 1
 """,
 "owner": "Finance Team",
 "update_frequency": "Daily at 00:00 UTC",
 "data_source": "PROD_DB.FINANCE.SUBSCRIPTIONS",
 "quality_checks": [
 "No negative values",
 "Month-over-month change < 50%",
 "Year-over-year growth between -20% and +100%"
 ],
 "related_metrics": ["annual_recurring_revenue", "customer_lifetime_value"]
 }
}

# Display in UI
def show_metric_definition(metric_key: str):
 metric = METRIC_DEFINITIONS[metric_key]
 with st.expander(f"ℹ️ About {metric['display_name']}"):
 st.write(f"**Definition:** {metric['definition']}")
 st.code(metric['calculation'], language='sql')
 st.caption(f"**Owner:** {metric['owner']}")
 st.caption(f"**Updated:** {metric['update_frequency']}")
 st.caption(f"**Source:** {metric['data_source']}")
```

### Calculation Transparency

**Show SQL logic for complex metrics:**
```python
st.metric("Customer Lifetime Value", f"${clv_value:.2f}")

with st.expander(" How is this calculated?"):
 st.markdown("""
 **Customer Lifetime Value (CLV) Calculation:**

 CLV = (Average Purchase Value × Purchase Frequency × Customer Lifespan)

 Where:
 - Average Purchase Value = Total Revenue / Number of Purchases
 - Purchase Frequency = Number of Purchases / Number of Unique Customers
 - Customer Lifespan = Average number of years a customer remains active
 """)

 st.code("""
 WITH customer_metrics AS (
 SELECT
 customer_id,
 AVG(purchase_amount) AS avg_purchase_value,
 COUNT(*) AS purchase_count,
 DATEDIFF('day', MIN(purchase_date), MAX(purchase_date)) / 365.25 AS lifespan_years
 FROM purchases
 GROUP BY customer_id
 )
 SELECT
 AVG(avg_purchase_value * purchase_count / NULLIF(lifespan_years, 0)) AS clv
 FROM customer_metrics;
 """, language='sql')
```
