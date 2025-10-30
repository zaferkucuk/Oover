# 🧪 Manual End-to-End Testing Guide for Teams API Integration

**Feature**: teams_api
**Phase**: 9.2 - End-to-End Testing
**Created**: 2025-10-30
**Purpose**: Validate teams API integration with real Football-Data.org API

---

## 📋 Prerequisites

### 1. Environment Setup
Ensure these environment variables are set in your `.env` file:

```bash
# Football-Data.org API
FOOTBALL_DATA_API_KEY=your_api_key_here

# Database
DATABASE_URL=your_supabase_url_here
```

### 2. Database State
- Supabase database is accessible
- Countries table is populated (96 countries)
- Leagues table has at least Premier League (PL)

### 3. Django Setup
- Backend is running
- Migrations are applied
- No pending database changes

---

## 🧪 Test Scenarios

### Test 1: Single League Fetch (Premier League)
**Purpose**: Test basic fetch operation with one league
**Expected Time**: ~30 seconds

```bash
# Navigate to backend directory
cd backend

# Run the command
python manage.py fetch_teams --league PL --provider football-data

# Expected Output:
# ✓ Fetching teams from leagues: PL
# ✓ Provider: football-data
# ✓ [1/1] Fetching teams for PL...
# ✓    ✓ X created, Y updated, 0 failed
# ✓ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✓ OPERATION SUMMARY
# ✓ Successfully processed 20 teams from API | X new teams created | Y teams updated
```

**Validation Checklist**:
- [ ] Command executes without errors
- [ ] Progress messages are displayed
- [ ] Statistics show created/updated counts
- [ ] No Python exceptions thrown

---

### Test 2: Multiple Leagues Fetch (European)
**Purpose**: Test multi-league processing and statistics aggregation
**Expected Time**: ~2 minutes

```bash
# Run with all European leagues
python manage.py fetch_teams --all-european --provider football-data

# Expected Output:
# ✓ Fetching teams from all European leagues...
# ✓ Provider: football-data
# ✓ 📋 Processing 5 European leagues: PL, PD, SA, BL1, FL1
# ✓ [1/5] Fetching teams for PL...
# ✓    ✓ X created, Y updated, 0 failed
# ✓ [2/5] Fetching teams for PD...
# ✓    ✓ X created, Y updated, 0 failed
# ✓ ... (continues for all leagues)
# ✓ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✓ OPERATION SUMMARY
# ✓ Successfully processed ~100 teams from API
```

**Validation Checklist**:
- [ ] All 5 leagues are processed
- [ ] Each league shows individual statistics
- [ ] Total statistics are aggregated correctly
- [ ] No duplicate teams created

---

### Test 3: Dry Run Mode
**Purpose**: Test validation without database writes
**Expected Time**: ~15 seconds

```bash
# Run in dry-run mode
python manage.py fetch_teams --league PL --dry-run

# Expected Output:
# ✓ ⚠️  DRY RUN MODE - No data will be saved
# ✓ Fetching teams from leagues: PL
# ✓ [1/1] Fetching teams for PL...
# ✓ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✓ DRY RUN COMPLETE - No changes made to database
```

**Validation Checklist**:
- [ ] Dry run warning is displayed
- [ ] No database writes occur
- [ ] Data validation still happens
- [ ] API is called normally

---

### Test 4: Error Handling (Invalid League)
**Purpose**: Test error handling with invalid input
**Expected Time**: ~5 seconds

```bash
# Try with invalid league code
python manage.py fetch_teams --league INVALID

# Expected Output:
# ✓ Fetching teams from leagues: INVALID
# ✓ Provider: football-data
# ✓ [1/1] Fetching teams for INVALID...
# ✓    ✗ Error fetching INVALID: [error message]
# ✓ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✓ OPERATION COMPLETED WITH ERRORS
```

**Validation Checklist**:
- [ ] Error is caught and displayed
- [ ] Command doesn't crash
- [ ] Meaningful error message shown
- [ ] Partial results still saved (if any)

---

### Test 5: Rate Limit Handling
**Purpose**: Test API rate limit handling (10 req/min for free tier)
**Expected Time**: ~1 minute

```bash
# Run multiple leagues to test rate limiting
python manage.py fetch_teams --league PL --league PD --league SA

# Expected Behavior:
# - May hit rate limit during execution
# - Should handle gracefully with retries or delays
# - Should not crash or lose data
```

**Validation Checklist**:
- [ ] Rate limit is detected
- [ ] Appropriate delays or retries happen
- [ ] All data is eventually fetched
- [ ] Clear messages about rate limiting

---

## 🔍 Database Validation

After running tests, verify database state:

### Check Teams Created
```sql
-- Connect to Supabase and run:
SELECT 
    t.name as team_name,
    t.short_name,
    t.code,
    c.name as country_name,
    t.api_football_id,
    t.football_data_id,
    t.created_at
FROM teams t
LEFT JOIN countries c ON t.country_id = c.id
WHERE t.created_at > NOW() - INTERVAL '1 hour'
ORDER BY t.created_at DESC
LIMIT 20;
```

**Expected Result**:
- New teams with proper country assignments
- Both API IDs populated (if available)
- Valid team names, codes
- Recent timestamps

---

### Check Country Matching
```sql
-- Verify country matching worked correctly
SELECT 
    c.name as country,
    COUNT(t.id) as team_count
FROM teams t
JOIN countries c ON t.country_id = c.id
WHERE t.created_at > NOW() - INTERVAL '1 hour'
GROUP BY c.name
ORDER BY team_count DESC;
```

**Expected Result**:
- England: ~20 teams (Premier League)
- Spain: ~20 teams (La Liga)
- Italy: ~20 teams (Serie A)
- Germany: ~18 teams (Bundesliga)
- France: ~20 teams (Ligue 1)

---

### Check API Operation Logs
```sql
-- Check operation records
SELECT 
    operation_type,
    status,
    teams_fetched,
    teams_created,
    teams_updated,
    teams_failed,
    provider,
    created_at,
    error_message
FROM api_operations
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

**Expected Result**:
- Operation records created
- Status = 'success' or 'completed'
- Statistics match command output
- No error messages (unless expected)

---

## ✅ Success Criteria

### Must Have (Critical)
- [ ] Command executes without Python exceptions
- [ ] Teams are created in database
- [ ] Country matching works (teams have valid country_id)
- [ ] Statistics are accurate
- [ ] API operation logs are created

### Should Have (Important)
- [ ] Progress messages are clear and informative
- [ ] Error handling is graceful
- [ ] Duplicate teams are handled (update, not create)
- [ ] Rate limiting is respected
- [ ] Dry-run mode works correctly

### Nice to Have (Optional)
- [ ] Performance is acceptable (<2 min for all leagues)
- [ ] Memory usage is reasonable
- [ ] Logs are detailed enough for debugging

---

## 🐛 Common Issues & Solutions

### Issue 1: "No Country Found for Code: GB"
**Cause**: Country mapping is incorrect or missing
**Solution**: 
```python
# Check country mapping in services/teams_service.py
# Verify GB -> United Kingdom mapping exists
```

### Issue 2: "Rate Limit Exceeded"
**Cause**: Too many API requests in short time
**Solution**:
```bash
# Wait 1 minute between test runs
# Or use smaller test set: --limit 5
```

### Issue 3: "API Key Invalid"
**Cause**: Environment variable not set or incorrect
**Solution**:
```bash
# Check .env file
echo $FOOTBALL_DATA_API_KEY
# Should output your actual API key
```

### Issue 4: "League Not Found"
**Cause**: League not in provider's response
**Solution**:
```bash
# Use correct league codes:
# PL (Premier League)
# PD (La Liga)
# SA (Serie A)
# BL1 (Bundesliga)
# FL1 (Ligue 1)
```

---

## 📊 Test Results Template

Copy this template and fill in after testing:

```markdown
## Test Results - [Date]

### Environment
- Backend Version: [git commit hash]
- Python Version: [version]
- Django Version: [version]
- Database: Supabase PostgreSQL

### Test 1: Single League (PL)
- Status: [ ] Pass / [ ] Fail
- Teams Fetched: [number]
- Teams Created: [number]
- Teams Updated: [number]
- Execution Time: [seconds]
- Notes: [any observations]

### Test 2: All European Leagues
- Status: [ ] Pass / [ ] Fail
- Total Teams Fetched: [number]
- Total Teams Created: [number]
- Total Teams Updated: [number]
- Execution Time: [seconds]
- Notes: [any observations]

### Test 3: Dry Run
- Status: [ ] Pass / [ ] Fail
- Database Changes: [should be 0]
- Notes: [any observations]

### Test 4: Error Handling
- Status: [ ] Pass / [ ] Fail
- Error Message Quality: [good/needs improvement]
- Notes: [any observations]

### Test 5: Rate Limiting
- Status: [ ] Pass / [ ] Fail
- Rate Limit Hit: [ ] Yes / [ ] No
- Handling: [describe how it was handled]
- Notes: [any observations]

### Database Validation
- Teams in DB: [ ] Correct / [ ] Issues
- Country Matching: [ ] Working / [ ] Issues
- API Operation Logs: [ ] Created / [ ] Missing
- Notes: [any observations]

### Overall Result
- [ ] All tests passed
- [ ] Some tests failed (list below)
- [ ] Major issues found (describe)

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
1. [Recommendation]
2. [Recommendation]
```

---

## 🎯 Next Steps After Testing

### If All Tests Pass
1. Mark Phase 9.2 as complete
2. Update PROJECT_STATUS.md
3. Commit test results
4. Move to documentation or next feature

### If Tests Fail
1. Document specific failures
2. Create bug fix tasks
3. Prioritize critical issues
4. Re-run tests after fixes

---

**Last Updated**: 2025-10-30
**Maintainer**: Oover Development Team
**Related Docs**: 
- `PROJECT_STATUS.md`
- `backend/api_integrations/README.md`
- `backend/api_integrations/services/teams_service.py`
