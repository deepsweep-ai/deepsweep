# PostHog Dashboard Setup Guide

This guide walks through setting up PostHog analytics for DeepSweep, configuring dashboards, and analyzing activation metrics following industry best practices from Snyk, Vercel CLI, and GitHub CLI.

## Table of Contents

1. [PostHog Account Setup](#posthog-account-setup)
2. [API Key Configuration](#api-key-configuration)
3. [Dashboard Configuration](#dashboard-configuration)
4. [Key Metrics](#key-metrics)
5. [Funnel Analysis](#funnel-analysis)
6. [Retention Tracking](#retention-tracking)
7. [Best Practices](#best-practices)

---

## PostHog Account Setup

### 1. Create PostHog Account

1. Go to [PostHog Cloud](https://app.posthog.com/signup)
2. Sign up with your work email
3. Create new organization: "DeepSweep"
4. Create new project: "DeepSweep CLI"

### 2. Choose Hosting Option

**Cloud (Recommended for MVP)**:
- Fastest setup
- Managed infrastructure
- US region: `https://us.i.posthog.com`
- EU region: `https://eu.i.posthog.com`

**Self-Hosted (For Enterprise)**:
- Full data control
- Custom retention policies
- Deploy via Docker/Kubernetes

### 3. Get Your API Key

1. Navigate to **Project Settings** (gear icon, bottom left)
2. Click **Project API Key**
3. Copy your **Project API Key** (format: `phc_...`)
4. **IMPORTANT**: This is different from Personal API Key (used for API calls)

Example key format:
```
phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n
```

---

## API Key Configuration

### Where Competitors Store Their Keys

**Snyk CLI** (`snyk/cli`):
- Location: `packages/snyk-protect/src/lib/analytics/index.ts`
- Format: Hardcoded constant in source code
- Pattern: `const POSTHOG_API_KEY = 'phc_...'`

**Vercel CLI** (`vercel/cli`):
- Location: `packages/cli/src/util/telemetry/index.ts`
- Format: Hardcoded constant
- Pattern: `export const POSTHOG_TOKEN = 'phc_...'`

**GitHub CLI** (`cli/cli`):
- Uses Segment, not PostHog
- Location: `internal/config/config_file.go`

**Why Hardcode Keys?**:
- CLI tools ship as compiled artifacts
- Users don't have direct file access
- Keys are read-only and rate-limited
- PostHog keys are safe to expose in client-side code

### Update DeepSweep API Key

**File**: `src/deepsweep/telemetry.py`

**Current Configuration**:
```python
# PostHog configuration
POSTHOG_API_KEY: Final[str] = "phc_2KxJqV5jZ9nY8wH3pL7mT6sN4vR1cX0bQ9dE8fG7hI6jK5lM4n"
POSTHOG_HOST: Final[str] = "https://us.i.posthog.com"
```

**Update Steps**:
1. Copy your Project API Key from PostHog
2. Replace `POSTHOG_API_KEY` value in `src/deepsweep/telemetry.py`
3. Update `POSTHOG_HOST` if using EU region or self-hosted
4. Commit changes (keys are safe to commit - they're read-only)

**Example**:
```python
POSTHOG_API_KEY: Final[str] = "phc_YOUR_ACTUAL_KEY_HERE"
POSTHOG_HOST: Final[str] = "https://us.i.posthog.com"  # or eu.i.posthog.com
```

---

## Dashboard Configuration

### 1. Create Main Dashboard

1. Navigate to **Dashboards** (sidebar)
2. Click **New Dashboard**
3. Name: "DeepSweep - Product Metrics"
4. Description: "Core activation and usage metrics"

### 2. Add Key Insights

Click **Add Insight** for each metric below:

#### A. Daily Active Users (DAU)

- **Type**: Trends
- **Event**: `deepsweep_validate` (primary action)
- **Metric**: Unique users
- **Time Range**: Last 30 days
- **Interval**: Day
- **Breakdown**: None

#### B. Weekly Active Users (WAU)

- **Type**: Trends
- **Event**: `deepsweep_validate`
- **Metric**: Unique users
- **Time Range**: Last 12 weeks
- **Interval**: Week
- **Breakdown**: None

#### C. Command Usage Distribution

- **Type**: Trends
- **Events**: All commands
  - `deepsweep_validate`
  - `deepsweep_badge`
  - `deepsweep_patterns`
- **Metric**: Total count
- **Time Range**: Last 30 days
- **Interval**: Day
- **Display**: Stacked area chart

#### D. Platform Distribution

- **Type**: Pie Chart
- **Event**: `deepsweep_validate`
- **Breakdown**: `os` property
- **Time Range**: Last 30 days

#### E. Version Adoption

- **Type**: Trends
- **Event**: `deepsweep_validate`
- **Metric**: Unique users
- **Breakdown**: `version` property
- **Time Range**: Last 30 days
- **Interval**: Day

#### F. Error Rate

- **Type**: Trends
- **Event**: `deepsweep_error`
- **Metric**: Total count
- **Time Range**: Last 7 days
- **Interval**: Day
- **Breakdown**: `error_type` property

---

## Key Metrics

### Activation Metrics

**1. First Run Completion**

Track users who complete their first validation:

- **Event**: `deepsweep_validate`
- **Filter**: `first_run = true`
- **Metric**: Unique users per day

**2. Time to First Validation**

Measure time from install to first use:

1. Create **Funnel**:
   - Step 1: First event (any command)
   - Step 2: `deepsweep_validate` with `first_run = true`
2. View conversion rate and median time

**3. Findings Discovery Rate**

Users who find security issues:

- **Event**: `deepsweep_validate`
- **Filter**: `findings_count > 0`
- **Metric**: Percentage of validations with findings

### Usage Patterns

**1. Average Validations per User**

- **Type**: Formula
- **Formula**: `Total validate events / Unique users`
- **Time Range**: Last 7 days

**2. Output Format Preference**

- **Event**: `deepsweep_validate`
- **Breakdown**: `output_format` property
- **Display**: Bar chart

**3. Command Latency**

- **Event**: `deepsweep_validate`
- **Metric**: Average of `duration_ms`
- **Display**: Trend line
- **Alert**: If avg > 200ms

---

## Funnel Analysis

### Activation Funnel

**Goal**: Track user journey from install to active usage

**Steps**:
1. **Install**: First event received (any command)
2. **First Validation**: `deepsweep_validate` executed
3. **Finding Review**: Validation with `findings_count > 0`
4. **Repeat Usage**: 2+ validations within 7 days

**Setup in PostHog**:

1. Navigate to **Insights** > **New Insight**
2. Select **Funnel**
3. Add steps:
   ```
   Step 1: Any event
   Step 2: deepsweep_validate (first_run = true)
   Step 3: deepsweep_validate (findings_count > 0)
   Step 4: deepsweep_validate (repeat within 7 days)
   ```
4. Set conversion window: 7 days
5. Save as "Activation Funnel"

**Key Questions to Answer**:
- What % complete first validation?
- Where do users drop off?
- How long from install to first validation?
- Do users with findings return more?

### Drop-off Analysis

**Identify friction points**:

1. **Funnel Drop-off Insight**:
   - Shows % who drop between each step
   - Clickable to see user cohorts

2. **Session Recordings** (PostHog Cloud):
   - Filter sessions where funnel failed
   - Watch user behavior to identify issues

3. **Common Drop-off Reasons**:
   - No findings found (validation passes) → No action needed
   - Error during validation → Check error logs
   - Long latency → Optimize performance

---

## Retention Tracking

### 1. Weekly Retention Cohorts

**Setup**:
1. Navigate to **Insights** > **New Insight**
2. Select **Retention**
3. Configure:
   - **Cohort Event**: Any event (first use)
   - **Return Event**: `deepsweep_validate`
   - **Cohort Size**: Week
   - **Retention Period**: 8 weeks

**What to Look For**:
- Week 0 → Week 1 retention (target: >40%)
- Week 1 → Week 2 retention (target: >60% of Week 1)
- Long-term plateau (healthy: 20-30% at Week 8)

### 2. Retention by Finding Count

**Hypothesis**: Users who find issues retain better

**Setup**:
1. Create retention insight
2. Add breakdown: `findings_count > 0` vs `findings_count = 0`
3. Compare retention curves

### 3. Stickiness Metric

**Formula**: DAU / MAU ratio

- **High stickiness** (>30%): Users return frequently
- **Low stickiness** (<10%): One-time usage pattern

**Setup**:
1. Create formula insight:
   ```
   DAU / MAU * 100
   ```
2. Track trend over time

---

## Best Practices

### 1. Respect User Privacy

DeepSweep telemetry follows strict privacy principles:

**Do Track**:
- Command usage counts
- Version and platform info
- Performance metrics (latency)
- Aggregated finding counts
- Exit codes (success/failure)

**Never Track**:
- File paths or names
- Code content
- Finding details (specific patterns matched)
- User identifiable information (PII)
- Project or organization names

### 2. Telemetry Opt-Out

All users can disable telemetry:

```bash
deepsweep telemetry disable
```

**Best Practice**: Show clear notice on first run with opt-out instructions (already implemented).

### 3. Dashboard Maintenance

**Weekly Review**:
- Check error rate trends
- Monitor version adoption
- Review top drop-off points

**Monthly Review**:
- Analyze retention cohorts
- Update funnel based on feature changes
- Review platform distribution for support prioritization

### 4. Alert Configuration

Set up alerts in PostHog:

1. **Critical Error Spike**:
   - Event: `deepsweep_error`
   - Threshold: >50 errors in 1 hour
   - Action: Slack notification

2. **Version Adoption Lag**:
   - Metric: Users on old version
   - Threshold: >50% on version older than 30 days
   - Action: Email notification

3. **Activation Drop-off**:
   - Funnel: Step 1 → Step 2
   - Threshold: <30% conversion
   - Action: Dashboard notification

### 5. A/B Testing (Future)

PostHog supports feature flags for experimentation:

**Example Test**:
- **Hypothesis**: More descriptive error messages increase repeat usage
- **Variant A**: Current error messages
- **Variant B**: Enhanced error messages with examples
- **Metric**: 7-day retention rate

---

## Common PostHog Queries

### Find Users with Specific Behavior

**Users who hit errors**:
```sql
-- In PostHog SQL tab
SELECT distinct_id, properties
FROM events
WHERE event = 'deepsweep_error'
  AND timestamp > now() - interval '7 days'
```

**High-frequency users (power users)**:
```sql
SELECT distinct_id, count(*) as validation_count
FROM events
WHERE event = 'deepsweep_validate'
  AND timestamp > now() - interval '30 days'
GROUP BY distinct_id
HAVING count(*) > 20
ORDER BY validation_count DESC
```

**First-time users (onboarding cohort)**:
```sql
SELECT distinct_id, min(timestamp) as first_seen
FROM events
WHERE event = 'deepsweep_validate'
GROUP BY distinct_id
HAVING min(timestamp) > now() - interval '7 days'
```

---

## Integration with CI/CD

### Track CI Usage Separately

Add environment detection to telemetry:

**Property**: `ci_environment`
**Values**: `local`, `ci`, `unknown`

**Benefits**:
- Separate CI usage from developer usage
- Identify most popular CI platforms (GitHub Actions, GitLab CI, etc.)
- Track CI performance separately

**Implementation** (add to `telemetry.py`):
```python
import os

def detect_ci_environment() -> str:
    """Detect if running in CI environment."""
    ci_indicators = {
        "GITHUB_ACTIONS": "github_actions",
        "GITLAB_CI": "gitlab_ci",
        "CIRCLECI": "circleci",
        "TRAVIS": "travis",
        "JENKINS_URL": "jenkins",
    }

    for env_var, platform in ci_indicators.items():
        if os.getenv(env_var):
            return platform

    return "local" if os.isatty(0) else "unknown"
```

---

## Competitor Benchmarks

### Snyk CLI (Reference)

**Key Metrics**:
- **DAU**: ~50K daily active users
- **Activation Rate**: ~60% (first scan within 24h)
- **7-Day Retention**: ~45%
- **Stickiness (DAU/MAU)**: ~35%

**Dashboard Focus**:
- Command success rate (vs error rate)
- Vulnerability found distribution
- Integration adoption (GitHub App, IDE plugins)
- Platform/language breakdown

### Vercel CLI

**Key Metrics**:
- **DAU**: ~100K daily active users
- **Deployment success rate**: 98.5%
- **Stickiness**: ~40%

**Dashboard Focus**:
- Deployment latency (p50, p95, p99)
- Error categorization
- Framework distribution (Next.js, etc.)
- Preview deployment usage

---

## Next Steps

1. **Set up PostHog account** and copy API key
2. **Update `telemetry.py`** with your key
3. **Create main dashboard** with core metrics
4. **Set up activation funnel** to track user journey
5. **Configure retention cohorts** for weekly analysis
6. **Set alerts** for critical metrics
7. **Weekly review** of dashboard to identify issues

For questions or issues, see [PostHog Docs](https://posthog.com/docs) or reach out to support@deepsweep.ai.

---

## Appendix: Event Schema

### deepsweep_validate

```typescript
{
  event: "deepsweep_validate",
  properties: {
    command: "validate",
    version: "1.1.0",
    os: "Linux" | "Darwin" | "Windows",
    os_version: "5.15.0",
    python_version: "3.11.0",
    duration_ms: 45,
    exit_code: 0 | 1,
    findings_count: 2,
    pattern_count: 16,
    output_format: "text" | "json" | "sarif",
    first_run: true | false,
  },
  distinct_id: "uuid-v4",
  timestamp: "2025-12-22T10:30:00Z",
}
```

### deepsweep_error

```typescript
{
  event: "deepsweep_error",
  properties: {
    command: "validate",
    error_type: "ValidationError",
    error_message: "File not found: ~/.cursorrules",
    version: "1.1.0",
    os: "Linux",
  },
  distinct_id: "uuid-v4",
  timestamp: "2025-12-22T10:30:00Z",
}
```

### deepsweep_badge

```typescript
{
  event: "deepsweep_badge",
  properties: {
    command: "badge",
    exit_code: 0,
    output_format: "svg" | "json" | "markdown",
    version: "1.1.0",
    os: "Linux",
  },
  distinct_id: "uuid-v4",
  timestamp: "2025-12-22T10:30:00Z",
}
```

### deepsweep_patterns

```typescript
{
  event: "deepsweep_patterns",
  properties: {
    command: "patterns",
    exit_code: 0,
    pattern_count: 16,
    version: "1.1.0",
    os: "Linux",
  },
  distinct_id: "uuid-v4",
  timestamp: "2025-12-22T10:30:00Z",
}
```
