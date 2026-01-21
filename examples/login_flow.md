# Login Flow Testing Example

This example demonstrates how to automate a login flow test using the Android automation skill.

## Scenario

Test a login form with email and password fields, then verify successful login.

## Steps

```bash
# 1. Launch the app
python scripts/app/app_launch.py --package com.example.myapp --clear

# 2. Wait for app to load and map the screen
sleep 2
python scripts/interaction/screen_mapper.py --clickable

# 3. Find and tap the email field, then enter email
python scripts/interaction/navigator.py \
  --find-class EditText \
  --index 0 \
  --enter-text "testuser@example.com"

# 4. Find password field and enter password  
python scripts/interaction/navigator.py \
  --find-class EditText \
  --index 1 \
  --enter-text "SecurePass123!"

# 5. Tap the login button
python scripts/interaction/navigator.py \
  --find-text "Login" \
  --tap

# 6. Wait for navigation and verify success
sleep 3
python scripts/interaction/screen_mapper.py | grep -i "welcome\|dashboard\|home"

# 7. Take screenshot for documentation
python scripts/interaction/screenshot.py --output login_success.png
```

## Alternative: Using Resource IDs

If you know the resource IDs, use them for more reliable element selection:

```bash
# Enter email by ID
python scripts/interaction/navigator.py \
  --find-id "email_input" \
  --enter-text "testuser@example.com"

# Enter password by ID  
python scripts/interaction/navigator.py \
  --find-id "password_input" \
  --enter-text "SecurePass123!"

# Tap login by ID
python scripts/interaction/navigator.py \
  --find-id "login_button" \
  --tap
```

## Error Handling

If login fails, capture the state for debugging:

```bash
python scripts/testing/app_state.py \
  --package com.example.myapp \
  --output debug_login_failure/
```

## Accessibility Check

Verify the login form is accessible:

```bash
python scripts/testing/accessibility_audit.py --format text
```
