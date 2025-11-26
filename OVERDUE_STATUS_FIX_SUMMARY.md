# Overdue Status Bug Fix Summary

## Problem
Orders were not being marked as overdue even after 9+ working hours. The overdue status feature was completely broken.

## Root Causes Found

### **Bug #1: Function Signature Mismatch** ❌ FIXED
The `_mark_overdue_orders()` function was defined **without parameters** but called **with parameters** in two places:

```python
# Definition (line 49):
def _mark_overdue_orders():  # ← No parameters!

# Problematic calls:
_mark_overdue_orders(hours=24)             # Line 2689 ❌
_mark_overdue_orders(hours=overdue_hours)  # Line 4771 ❌
```

**Impact**: 
- Python raised `TypeError: _mark_overdue_orders() got an unexpected keyword argument 'hours'`
- Exception was caught and silently logged
- **Orders never got marked as overdue** ❌

### **Bug #2: Missing Parameter Support** ❌ FIXED
The two different call patterns suggested the function should support:
- **9 hours** (working hours threshold: 8 AM - 5 PM)
- **24 hours** (calendar hours for notification summaries)

But the function always used 9 hours and didn't accept customization.

## The Fix

### Fixed Function Signature
```python
def _mark_overdue_orders(hours: int = 9):
    """
    Mark orders as overdue based on time elapsed.
    
    Args:
        hours (int): Threshold in hours to mark orders as overdue.
                    - 9: Use working hours calculation (8 AM - 5 PM)
                    - 24: Use calendar hours (24-hour elapsed time)
                    Default: 9 (working hours)
    """
```

### How It Works Now

#### Mode 1: Working Hours (9 hours default)
- Uses `is_order_overdue()` which counts only 8 AM - 5 PM
- Example: Order created at 10 AM Day 1 → overdue at 10 AM Day 2 (9 working hours elapsed)
- **Called by**: Middleware and API endpoints for real-time overdue marking

#### Mode 2: Calendar Hours (24+ hours)
- Uses simple elapsed time: `now - timedelta(hours=24)`
- Example: Order created 24+ calendar hours ago → mark as stale
- **Called by**: Notification summary endpoint for showing old in-progress orders

## Working Hours Calculation

The system uses **9-hour working day** (8 AM - 5 PM):

```python
WORK_START_HOUR = 8    # 8:00 AM
WORK_END_HOUR = 17     # 5:00 PM
WORKING_HOURS_PER_DAY = 9  # 8 AM to 5 PM = 9 hours
OVERDUE_THRESHOLD_HOURS = 9
```

**Example Timeline**:
- **Day 1, 10:00 AM**: Order created
  - Working hours: 0 (just created)
  - Status: `created`
  
- **Day 1, 3:00 PM**: Same order still in progress (5 hours elapsed)
  - Working hours: 5 (10 AM - 5 PM)
  - Status: `in_progress`
  
- **Day 2, 10:00 AM**: Same order still in progress
  - Working hours: 9 (yesterday 10 AM - 5 PM = 7h, today 8 AM - 10 AM = 2h)
  - Status: **`overdue`** ✓
  
- **Day 2, 5:00 PM**: Same order still in progress
  - Working hours: 16 (yesterday 10 AM - 5 PM = 7h, today 8 AM - 5 PM = 9h)
  - Status: **`overdue`** ✓

## Where Overdue Marking Happens

1. **Middleware** (`tracker/middleware.py` line 43-56)
   - Runs on every request
   - Marks orders overdue when they exceed 9 working hours
   - Called with default `hours=9` (working hours)

2. **API Endpoints**
   - `api_order_status()` - Get single order status
   - `api_orders_statuses()` - Get multiple order statuses
   - Called with default `hours=9` (working hours)

3. **Orders List View** (`orders_list()` line 2689)
   - Called with `hours=24` for filtering "old" in-progress orders
   - Marks calendar-old orders (>24h) as stale for display

4. **Notification Summary** (`api_notifications_summary()` line 4771)
   - Called with customizable `hours` parameter from GET request
   - Used to show "stale orders" in header dropdown

## Files Modified
- `tracker/views.py` - Lines 49-119: Fixed `_mark_overdue_orders()` function to accept `hours` parameter

## Testing Verification

The system now correctly:
- ✅ Marks orders overdue after **9 working hours** (8 AM - 5 PM)
- ✅ Respects non-working hours (nights, weekends)
- ✅ Accepts custom hour thresholds for different use cases
- ✅ No more silent failures from TypeError
- ✅ Can mark "stale" orders (>24h) separately from working-hour overdue

## Related Code
- Working hours calculation: `tracker/utils/time_utils.py`
- Overdue check function: `is_order_overdue()` 
- Middleware auto-progress: `tracker/middleware.py`
