# Fix Spam Enter & Limit to 10 Questions

## Issues to Fix
1. Completion screen not appearing after 10 words
2. Enter key can be spammed, allowing more than 10 submissions

## Plan
- Add anti-spam protection with `isSubmitting` flag
- Add validation to prevent exceeding daily goal
- Disable input/button after goal reached
- Add Enter key debouncing
- Ensure completion screen shows properly

## Steps
- [x] Add `isSubmitting` flag to `CyberSRSApp` constructor
- [x] Modify `submitAnswer()` to check `isSubmitting` and goal limit
- [x] Update `completeSession()` to disable UI elements
- [x] Add debouncing to Enter key handler
- [x] Test: Spam Enter → only 1 submission processed
- [x] Test: After 10 words → input disabled, completion screen shows
- [x] Test: Cannot reach 11/10
