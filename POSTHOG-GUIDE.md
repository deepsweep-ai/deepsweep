# PostHog Analytics Guide - DeepSweep Telemetry

## Overview

DeepSweep uses a two-tier telemetry system. This guide covers the **Optional Tier (PostHog)** for product analytics.

### Telemetry Tiers

1. **Essential Tier (Always Active)** - Threat Intelligence
   - Powers community security signals
   - Sent to: `https://api.deepsweep.ai/v1/signal`
   - Cannot be disabled (core product value)

2. **Optional Tier (User Controlled)** - PostHog Analytics
   - Product analytics and metrics
   - Sent to: PostHog US Cloud
   - Can be disabled anytime

---

## PostHog Configuration

### Connection Details

```
PostHog Host: https://us.i.posthog.com
PostHog API Key: phc_yaXDgwcs2rJS84fyVQJg0QVlWdqEaFgpjiG47kLzL1l
Project: DeepSweep (US Region)
```

### Accessing PostHog Dashboard

**Option 1: Direct URL**
```
https://us.posthog.com/
```

**Option 2: Main PostHog Site**
1. Go to https://posthog.com/
2. Click "Login" (top right)
3. Select your organization
4. Navigate to the DeepSweep project

### Login Credentials

You'll need the PostHog account credentials associated with this project. If you don't have access:
- Contact the DeepSweep team admin
- Or check your password manager for PostHog credentials

---

## Events Being Tracked

### 1. Command Events

DeepSweep sends an event for each CLI command executed:

#### Event: `deepsweep_validate`
Triggered when: `deepsweep validate` is run

**Properties:**
```json
{
  "command": "validate",
  "version": "0.1.1",
  "os": "Darwin|Linux|Windows",
  "os_version": "...",
  "python_version": "3.10.x",
  "duration_ms": 1234,
  "exit_code": 0,
  "first_run": false,
  "findings_count": 0,
  "pattern_count": 16,
  "output_format": "text|json|sarif",
  "score": 100,
  "grade": "A"
}
```

#### Event: `deepsweep_badge`
Triggered when: `deepsweep badge` is run

**Properties:**
```json
{
  "command": "badge",
  "version": "0.1.1",
  "os": "Darwin|Linux|Windows",
  "os_version": "...",
  "python_version": "3.10.x",
  "duration_ms": 567,
  "exit_code": 0,
  "first_run": false,
  "output_format": "svg"
}
```

#### Event: `deepsweep_patterns`
Triggered when: `deepsweep patterns` is run

**Properties:**
```json
{
  "command": "patterns",
  "version": "0.1.1",
  "os": "Darwin|Linux|Windows",
  "os_version": "...",
  "python_version": "3.10.x",
  "duration_ms": 123,
  "exit_code": 0,
  "first_run": false,
  "pattern_count": 16
}
```

#### Event: `deepsweep_telemetry`
Triggered when: `deepsweep telemetry` commands are run

#### Event: `deepsweep_version`
Triggered when: `deepsweep version` is run

### 2. Error Events

#### Event: `deepsweep_error`
Triggered when: Any command encounters an error

**Properties:**
```json
{
  "command": "validate",
  "error_type": "FileNotFoundError",
  "error_message": "Config file not found at ~/path...",
  "version": "0.1.1",
  "os": "Darwin|Linux|Windows"
}
```

### 3. User Identification

#### Event: `$identify`
Triggered when: CLI starts (first command in a session)

**Properties:**
```json
{
  "distinct_id": "anonymous-uuid-v4",
  "version": "0.1.1",
  "os": "Darwin|Linux|Windows",
  "os_version": "...",
  "python_version": "3.10.x"
}
```

---

## How to View Events in PostHog

### Step 1: Access the PostHog Dashboard

1. Go to https://us.posthog.com/ and login
2. Select the DeepSweep project

### Step 2: View Live Events

**Navigate to: Activity → Events**

This shows a real-time stream of all incoming events.

**Filters you can apply:**
- Event name (e.g., `deepsweep_validate`)
- Time range (Last hour, Last 24 hours, Last 7 days, etc.)
- Properties (e.g., `os = Darwin`, `version = 0.1.1`)
- User ID (distinct_id)

### Step 3: Create Insights

**Navigate to: Product Analytics → Insights → New Insight**

Common insights to create:

#### A. Total Validations Over Time
```
Event: deepsweep_validate
Aggregation: Total count
Time range: Last 30 days
Breakdown: None
```

#### B. Adoption by Operating System
```
Event: deepsweep_validate
Aggregation: Unique users
Breakdown: os
```

#### C. First-Run vs Returning Users
```
Event: deepsweep_validate
Aggregation: Total count
Breakdown: first_run
```

#### D. Security Score Distribution
```
Event: deepsweep_validate
Aggregation: Total count
Breakdown: grade (A, B, C, D, F)
```

#### E. Output Format Usage
```
Event: deepsweep_validate
Aggregation: Total count
Breakdown: output_format
```

#### F. Error Rate
```
Event: deepsweep_error
Aggregation: Total count
Time range: Last 7 days
Breakdown: error_type
```

### Step 4: Create Dashboards

**Navigate to: Dashboards → New Dashboard**

Combine multiple insights into a single view:

**Example Dashboard: "DeepSweep CLI Health"**
1. Total validations (last 7 days) - Trend
2. Active users (last 7 days) - Number
3. Average score - Number
4. OS distribution - Pie chart
5. Error rate - Trend
6. Command usage - Bar chart

### Step 5: Set Up Funnels

**Navigate to: Product Analytics → Funnels**

Track user journeys:

**Example Funnel: "First-Time User Activation"**
```
Step 1: deepsweep_validate (first_run = true)
Step 2: deepsweep_validate (first_run = false)
Step 3: deepsweep_badge
```

This shows how many first-time users return and eventually generate badges.

---

## Useful PostHog Features

### 1. Session Replay (If Enabled)
Not currently used, but could be enabled for web dashboard

### 2. Feature Flags (If Needed)
Create feature flags to control rollout:
- `enable-new-pattern-format`
- `experimental-sarif-v2`

### 3. Cohorts
Group users by behavior:
- "Power Users" - Users who run `deepsweep validate` > 10 times/week
- "Badge Generators" - Users who have run `deepsweep badge`
- "First Week Users" - Users created in last 7 days

### 4. Retention Analysis
**Navigate to: Product Analytics → Retention**

Track weekly/monthly retention of CLI usage.

### 5. Lifecycle Analysis
**Navigate to: Product Analytics → Lifecycle**

See new, returning, resurrecting, and dormant users.

---

## Key Metrics to Monitor

### Activation Metrics
- **First Validation Rate**: % of installs that run first validation
- **Time to First Validation**: How quickly after install
- **First Validation Success**: Exit code 0 on first run

### Engagement Metrics
- **Daily Active Users (DAU)**: Unique users per day
- **Weekly Active Users (WAU)**: Unique users per week
- **Validations per User**: Average validations per active user
- **Command Mix**: Distribution of validate/badge/patterns/etc

### Quality Metrics
- **Average Score**: Mean security score across all validations
- **Grade Distribution**: % of A/B/C/D/F grades
- **Findings Rate**: % of validations with findings > 0
- **Error Rate**: % of commands that result in errors

### Technical Metrics
- **OS Distribution**: macOS vs Linux vs Windows usage
- **Python Version Distribution**: 3.10 vs 3.11 vs 3.12 vs 3.13
- **Output Format Preference**: text vs json vs sarif
- **Command Duration**: p50, p95, p99 latency

### Retention Metrics
- **D1 Retention**: % of users who return day 1
- **D7 Retention**: % of users who return within 7 days
- **D30 Retention**: % of users who return within 30 days

---

## Example Queries

### SQL-like Queries in PostHog

PostHog uses ClickHouse under the hood. You can write custom queries:

**Navigate to: Product Analytics → SQL**

#### Query 1: Total Validations by Week
```sql
SELECT
  toStartOfWeek(timestamp) as week,
  count(*) as validations
FROM events
WHERE event = 'deepsweep_validate'
GROUP BY week
ORDER BY week DESC
```

#### Query 2: Average Score by OS
```sql
SELECT
  JSONExtractString(properties, 'os') as os,
  avg(JSONExtractInt(properties, 'score')) as avg_score
FROM events
WHERE event = 'deepsweep_validate'
  AND timestamp > now() - INTERVAL 30 DAY
GROUP BY os
```

#### Query 3: Error Frequency
```sql
SELECT
  JSONExtractString(properties, 'error_type') as error,
  count(*) as occurrences
FROM events
WHERE event = 'deepsweep_error'
  AND timestamp > now() - INTERVAL 7 DAY
GROUP BY error
ORDER BY occurrences DESC
```

---

## Testing Telemetry Locally

### Send Test Events

```bash
# Enable telemetry (if disabled)
deepsweep telemetry enable

# Run validation (sends deepsweep_validate event)
deepsweep validate .

# Check badge (sends deepsweep_badge event)
deepsweep badge --output test-badge.svg

# List patterns (sends deepsweep_patterns event)
deepsweep patterns

# Check telemetry status
deepsweep telemetry status
```

### View Your User ID

Your anonymous UUID is stored in:
```bash
cat ~/.deepsweep/config.json
```

Search for this UUID in PostHog to see all your events:
**Filter: distinct_id = "your-uuid-here"**

### Disable Telemetry

```bash
# Disable optional tier (PostHog)
deepsweep telemetry disable

# Enable offline mode (disables ALL telemetry)
export DEEPSWEEP_OFFLINE=1
deepsweep validate .
```

---

## Privacy & Compliance

### What IS Collected
- ✅ Anonymous UUID (cannot be reversed)
- ✅ Command usage (validate, badge, patterns)
- ✅ OS and Python version
- ✅ Security scores and grades
- ✅ Finding counts (number only)
- ✅ Pattern match counts
- ✅ Command duration and exit codes
- ✅ Error types (sanitized)

### What is NEVER Collected
- ❌ Source code or file contents
- ❌ File paths or repository names
- ❌ API keys, tokens, or secrets
- ❌ Personally identifiable information
- ❌ IP addresses (anonymized by PostHog)
- ❌ Email addresses or usernames
- ❌ Organization or project names

### GDPR Compliance
- Users can disable at any time: `deepsweep telemetry disable`
- Users can request data deletion (contact DeepSweep team)
- Data retention: 90 days (configurable in PostHog)

---

## Troubleshooting

### Events Not Showing Up

1. **Check telemetry is enabled:**
   ```bash
   deepsweep telemetry status
   ```
   Should show: "Optional tier enabled"

2. **Check not in offline mode:**
   ```bash
   echo $DEEPSWEEP_OFFLINE
   ```
   Should be empty or 0

3. **Check network connectivity:**
   PostHog events are sent async with 2-second timeout

4. **Check PostHog project:**
   Ensure you're viewing the correct project in the dashboard

5. **Wait for processing:**
   PostHog can take 1-2 minutes to process and display events

### Can't Access Dashboard

1. **Check login credentials:**
   - Email associated with PostHog account
   - Password or SSO

2. **Check organization access:**
   - You may need to be invited to the organization
   - Contact DeepSweep team admin

3. **Check PostHog region:**
   - US Cloud: https://us.posthog.com/
   - EU Cloud: https://eu.posthog.com/
   - DeepSweep uses US region

---

## Resources

- **PostHog Documentation**: https://posthog.com/docs
- **PostHog US Dashboard**: https://us.posthog.com/
- **DeepSweep Telemetry Docs**: https://docs.deepsweep.ai/telemetry
- **Privacy Policy**: https://deepsweep.ai/privacy

---

## Quick Reference

### Key URLs
- Dashboard: https://us.posthog.com/
- Live Events: https://us.posthog.com/events
- Insights: https://us.posthog.com/insights
- Dashboards: https://us.posthog.com/dashboard

### Key Events
- `deepsweep_validate` - Validation runs
- `deepsweep_badge` - Badge generation
- `deepsweep_patterns` - Pattern listings
- `deepsweep_error` - Error occurrences
- `$identify` - User identification

### Configuration
- Config file: `~/.deepsweep/config.json`
- Disable: `deepsweep telemetry disable`
- Enable: `deepsweep telemetry enable`
- Status: `deepsweep telemetry status`
- Offline: `export DEEPSWEEP_OFFLINE=1`
