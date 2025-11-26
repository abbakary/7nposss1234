# Overdue Calculation Simplified to 9 Calendar Hours

## What Changed
Replaced complex working hours calculation with simple 9-hour calendar threshold.

**Before**: Calculated working hours between 8 AM - 5 PM (9-hour workday), accounting for multiple days, weekends, etc.

**After**: Simple elapsed time check - if 9 calendar hours have passed since order start, mark as overdue.

## Why Simpler?
- **No day/date calculations**: Don't count days separately
- **No working hour boundaries**: Don't check if time falls between 8 AM - 5 PM
- **No complexity**: Just: `elapsed_hours = (now - started_at).total_seconds() / 3600.0`
- **Same threshold**: Still uses 9 hours, just simpler logic

## How It Works

### Example Timeline
```
10:00 AM Day 1: Order started
├── 3:00 PM Day 1: 5 hours elapsed → NOT overdue ✓
├── 7:00 AM Day 2: 21 hours elapsed → OVERDUE (>9h) ✓
├── 7:30 PM Day 1: 9.5 hours elapsed → OVERDUE ✓
└── 6:59 PM Day 1: 8.98 hours elapsed → NOT overdue ✓
```

### Simple Check
```python
elapsed_hours = (now - started_at).total_seconds() / 3600.0
is_overdue = elapsed_hours >= 9
```

## Code Changes

### 1. Simplified `time_utils.py`
**Removed** (no longer needed):
- `get_work_start_time()` - Get 8 AM for a date
- `get_work_end_time()` - Get 5 PM for a date
- `is_during_working_hours()` - Check if time is between 8 AM - 5 PM
- `calculate_working_hours_between()` - Complex multi-day working hour calculation (100+ lines)
- `calculate_estimated_duration()` - Was using working hours calc
- `format_working_hours()` → renamed to `format_hours()` (same functionality)

**Kept** (simple and useful):
- `is_order_overdue()` - 9 calendar hours check
- `get_order_overdue_status()` - Returns overdue status dict
- `format_hours()` - Format "9h 30m" style strings
- `estimate_completion_time()` - Estimate when order will be done
- `OVERDUE_THRESHOLD_HOURS` - Constant = 9

### 2. Simplified `views.py`
**Before**:
```python
def _mark_overdue_orders(hours: int = 9):
    if hours == 9:
        # Working hours calculation...
    else:
        # Calendar hours calculation...
```

**After**:
```python
def _mark_overdue_orders():
    """Mark orders overdue after 9 calendar hours elapsed."""
    # Single path: simple elapsed time check
```

**Removed**:
- `hours` parameter - always uses 9 calendar hours
- Conditional logic - no more if/else for different thresholds
- All calls updated to: `_mark_overdue_orders()` (no arguments)

### 3. Removed Unused Parameters
- Removed `overdue_hours` request parameter from `api_notifications_summary()`
- Hardcoded 24-hour cutoff for showing stale orders

## Performance
- **Faster**: No loops through dates and working hour boundaries
- **Memory efficient**: No complex date range calculations
- **Fewer database queries**: Can use simple timestamp comparison

## Testing

### Simple Test Cases
1. **Order created 8 hours ago** → NOT overdue ✓
2. **Order created 9 hours ago** → OVERDUE ✓
3. **Order created 24 hours ago** → OVERDUE ✓
4. **Order created this morning at 10 AM, now 10 PM same day** → OVERDUE ✓

## Files Modified
- `tracker/utils/time_utils.py` - Removed ~100 lines of complex logic
- `tracker/views.py` - Simplified `_mark_overdue_orders()` function

## What Still Works
- ✅ Orders marked as overdue in middleware
- ✅ Orders marked as overdue in views
- ✅ Overdue status returned in API responses
- ✅ Order detail pages show overdue status
- ✅ Dashboard metrics count overdue orders
- ✅ Notification summary includes overdue orders

## Summary
**Simpler, faster, and easier to understand**. Just checks: "Has 9 calendar hours passed?" No working hours complexity.
