"""
E2E Browser Automation Test Suite for DeshMrittika / BHUMI-SYNC v2.1
Uses Selenium WebDriver with Headless Google Chrome to verify all user journeys.
"""
import time
import json
import os
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:8000/"
SCREENSHOT_DIR = "/Users/macbookair/.gemini/antigravity-ide/brain/534f317e-4b5e-4d18-97af-bc7d845b3b49/browser_proofs"

class BrowserAuthE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1440,900')
        # Enable logging for browser console
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        # Open base URL and clear storage for isolated test
        self.driver.get(BASE_URL)
        self.driver.execute_script("localStorage.clear(); sessionStorage.clear();")
        self.driver.get(BASE_URL)
        time.sleep(0.5)
        # Navigate to landing view for testing landing auth modals
        self.driver.execute_script("if (window.navigateToLanding) window.navigateToLanding();")
        time.sleep(0.5)

    def test_01_landing_page_guest_state(self):
        """Verify landing page loads cleanly in guest mode with login and signup CTAs."""
        driver = self.driver
        # Check hero buttons
        hero_login = driver.find_element(By.XPATH, "//button[contains(., 'লগইন করুন')]")
        hero_signup = driver.find_element(By.XPATH, "//button[contains(., 'নতুন অ্যাকাউন্ট নিবন্ধন')]")
        self.assertTrue(hero_login.is_displayed(), "Hero login button should be visible")
        self.assertTrue(hero_signup.is_displayed(), "Hero signup button should be visible")

        # Check console logs for errors
        logs = driver.get_log('browser')
        severe_errors = [l for l in logs if l['level'] == 'SEVERE' and 'favicon' not in l['message']]
        self.assertEqual(len(severe_errors), 0, f"Unexpected JS console errors on landing: {severe_errors}")
        
        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "01_landing_guest.png"))

    def test_02_click_login_opens_auth_modal(self):
        """Verify clicking login button opens the auth modal in login view."""
        driver = self.driver
        hero_login = driver.find_element(By.XPATH, "//button[contains(., 'লগইন করুন')]")
        hero_login.click()
        time.sleep(0.5)

        auth_modal = driver.find_element(By.ID, "auth-modal")
        self.assertTrue(auth_modal.is_displayed(), "Auth modal must be visible on screen")
        self.assertIn("open", auth_modal.get_attribute("class"), "Modal must have 'open' class")

        login_view = driver.find_element(By.ID, "auth-view-login")
        self.assertTrue(login_view.is_displayed(), "Login view must be active")
        
        # Check inputs
        email_input = driver.find_element(By.ID, "login-email")
        password_input = driver.find_element(By.ID, "login-password")
        self.assertTrue(email_input.is_displayed())
        self.assertTrue(password_input.is_displayed())

        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "02_login_modal_opened.png"))

    def test_03_switch_between_login_and_signup(self):
        """Verify seamless switching between login and signup views."""
        driver = self.driver
        driver.execute_script("openAuthModal('login');")
        time.sleep(0.3)

        # Switch to signup
        switch_to_signup = driver.find_element(By.ID, "auth-switch-to-signup")
        switch_to_signup.click()
        time.sleep(0.3)

        signup_view = driver.find_element(By.ID, "auth-view-signup")
        login_view = driver.find_element(By.ID, "auth-view-login")
        self.assertTrue(signup_view.is_displayed(), "Signup view should be displayed")
        self.assertFalse(login_view.is_displayed(), "Login view should be hidden")

        # Verify signup form fields
        self.assertTrue(driver.find_element(By.ID, "signup-name").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "signup-email").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "signup-phone").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "signup-role").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "signup-password").is_displayed())
        self.assertTrue(driver.find_element(By.ID, "signup-confirm-password").is_displayed())

        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "03_signup_view_switched.png"))

        # Switch back to login
        switch_to_login = driver.find_element(By.ID, "auth-switch-to-login")
        switch_to_login.click()
        time.sleep(0.3)

        self.assertTrue(login_view.is_displayed(), "Login view should be visible again")
        self.assertFalse(signup_view.is_displayed(), "Signup view should be hidden again")

    def test_04_close_and_reopen_modal(self):
        """Verify modal can be closed via close button and reopened via signup button."""
        driver = self.driver
        driver.execute_script("openAuthModal('login');")
        time.sleep(0.3)

        # Close modal
        close_btn = driver.find_element(By.CSS_SELECTOR, ".auth-close-btn")
        close_btn.click()
        time.sleep(0.3)

        auth_modal = driver.find_element(By.ID, "auth-modal")
        self.assertNotIn("open", auth_modal.get_attribute("class"), "Modal should lose 'open' class")
        self.assertFalse(auth_modal.is_displayed(), "Modal should not be visible")

        # Click hero signup button
        hero_signup = driver.find_element(By.XPATH, "//button[contains(., 'নতুন অ্যাকাউন্ট নিবন্ধন')]")
        hero_signup.click()
        time.sleep(0.3)

        self.assertTrue(auth_modal.is_displayed(), "Modal should reopen")
        signup_view = driver.find_element(By.ID, "auth-view-signup")
        self.assertTrue(signup_view.is_displayed(), "Modal should open directly to signup view")

    def test_05_demo_login_citizen_and_logout(self):
        """Verify 1-click Citizen demo login routes to citizen dashboard and logout works."""
        driver = self.driver
        driver.execute_script("openAuthModal('login');")
        time.sleep(0.3)

        # Click Citizen demo button using exact ID
        demo_citizen_btn = driver.find_element(By.ID, "demo-login-citizen")
        demo_citizen_btn.click()
        time.sleep(1.5)

        # Auth modal should close
        auth_modal = driver.find_element(By.ID, "auth-modal")
        self.assertFalse(auth_modal.is_displayed(), "Modal should close after demo login")

        # Topbar user button should show logged in user
        user_pill = driver.find_element(By.ID, "topbar-user-btn")
        self.assertTrue(user_pill.is_displayed(), "User button should be displayed in topbar")
        self.assertIn("নাগরিক", user_pill.text, "User button should display citizen role")

        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "05_citizen_dashboard_active.png"))

        # Open Profile drawer
        user_pill.click()
        time.sleep(0.5)

        profile_modal = driver.find_element(By.ID, "user-profile-modal")
        self.assertTrue(profile_modal.is_displayed(), "Profile modal should open")

        # Logout
        logout_btn = driver.find_element(By.ID, "profile-logout-btn")
        logout_btn.click()
        time.sleep(0.5)
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(1)

        # User button should now be hidden or guest mode active
        self.assertFalse(user_pill.is_displayed(), "User button should be hidden after logout")
        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "05_logout_successful.png"))

    def test_06_demo_login_admin_access(self):
        """Verify 1-click Admin demo login grants Admin workspace access."""
        driver = self.driver
        driver.execute_script("openAuthModal('login');")
        time.sleep(0.3)

        # Click Admin demo button using exact ID
        demo_admin_btn = driver.find_element(By.ID, "demo-login-admin")
        demo_admin_btn.click()
        time.sleep(1.5)

        # User button should show Admin
        user_pill = driver.find_element(By.ID, "topbar-user-btn")
        self.assertTrue(user_pill.is_displayed())
        self.assertIn("অ্যাডমিন", user_pill.text)

        # Admin nav items should be visible
        admin_nav_users = driver.find_element(By.ID, "nav-item-users")
        admin_nav_logs = driver.find_element(By.ID, "nav-item-security-logs")
        self.assertTrue(admin_nav_users.is_displayed(), "Admin users nav item should be visible")
        self.assertTrue(admin_nav_logs.is_displayed(), "Admin security logs nav item should be visible")

        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "06_admin_dashboard_active.png"))

        # Logout
        user_pill.click()
        time.sleep(0.5)
        logout_btn = driver.find_element(By.ID, "profile-logout-btn")
        logout_btn.click()
        time.sleep(0.5)
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(1)

    def test_07_signup_with_valid_input_and_otp_view(self):
        """Verify signup flow creates account and transitions to OTP verification view."""
        driver = self.driver
        driver.execute_script("openAuthModal('signup');")
        time.sleep(0.3)

        test_email = f"e2e_user_{int(time.time())}@example.com"
        driver.find_element(By.ID, "signup-name").send_keys("মো: টেস্ট ইউজার")
        driver.find_element(By.ID, "signup-email").send_keys(test_email)
        driver.find_element(By.ID, "signup-phone").send_keys("01799887766")
        driver.find_element(By.ID, "signup-password").send_keys("Password123!")
        driver.find_element(By.ID, "signup-confirm-password").send_keys("Password123!")
        
        # Agree to terms
        terms_checkbox = driver.find_element(By.ID, "signup-terms")
        if not terms_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", terms_checkbox)

        # Submit signup
        signup_submit_btn = driver.find_element(By.ID, "signup-submit-btn")
        signup_submit_btn.click()
        time.sleep(1.5)

        # Verify OTP view is displayed
        otp_view = driver.find_element(By.ID, "auth-view-otp")
        self.assertTrue(otp_view.is_displayed(), "OTP verification view should be visible")

        # Verify email badge in OTP view
        email_badge = driver.find_element(By.ID, "otp-target-email-badge")
        self.assertEqual(email_badge.text, test_email)

        # Verify 6 digit inputs are present
        for i in range(1, 7):
            digit_input = driver.find_element(By.ID, f"otp-digit-{i}")
            self.assertTrue(digit_input.is_displayed())

        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "07_otp_view_active.png"))

    def test_08_invalid_otp_rejection(self):
        """Verify submitting invalid OTP shows alert / error and prevents login."""
        driver = self.driver
        driver.execute_script("openAuthModal('signup');")
        time.sleep(0.3)

        # Enter signup details
        test_email = f"e2e_otp_test_{int(time.time())}@example.com"
        driver.find_element(By.ID, "signup-name").send_keys("ওটিপি পরীক্ষক")
        driver.find_element(By.ID, "signup-email").send_keys(test_email)
        driver.find_element(By.ID, "signup-phone").send_keys("01711223344")
        driver.find_element(By.ID, "signup-password").send_keys("Password123!")
        driver.find_element(By.ID, "signup-confirm-password").send_keys("Password123!")
        driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "signup-terms"))
        driver.find_element(By.ID, "signup-submit-btn").click()
        time.sleep(1.5)

        # Fill wrong digits 0 0 0 0 0 0
        for i in range(1, 7):
            driver.find_element(By.ID, f"otp-digit-{i}").send_keys("0")

        # Submit OTP
        driver.find_element(By.ID, "otp-verify-btn").click()
        time.sleep(1.0)

        # Check for alert dialog
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            self.assertIn("অকার্যকর", alert_text)
        except Exception:
            # If no browser alert, verify OTP view remains active and user is not logged in
            self.assertTrue(driver.find_element(By.ID, "auth-view-otp").is_displayed())

        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "08_invalid_otp_rejected.png"))

    def test_09_empty_form_submission_validation(self):
        """Verify empty login form fails HTML5 / JS validation and blocks submission."""
        driver = self.driver
        driver.execute_script("openAuthModal('login');")
        time.sleep(0.3)

        email_input = driver.find_element(By.ID, "login-email")
        password_input = driver.find_element(By.ID, "login-password")
        email_input.clear()
        password_input.clear()

        # Check HTML5 validation state
        is_email_valid = driver.execute_script("return document.getElementById('login-email').validity.valid;")
        self.assertFalse(is_email_valid, "Empty required email should be invalid")

        # Submit button click should not navigate or close modal
        driver.find_element(By.ID, "login-submit-btn").click()
        time.sleep(0.5)

        auth_modal = driver.find_element(By.ID, "auth-modal")
        self.assertTrue(auth_modal.is_displayed(), "Modal should remain open on empty submission")

    def test_10_invalid_login_shows_safe_error(self):
        """Verify submitting invalid credentials triggers safe error alert and remains on login form."""
        driver = self.driver
        driver.execute_script("openAuthModal('login');")
        time.sleep(0.3)

        driver.find_element(By.ID, "login-email").send_keys("nonexistent_user@deshmrittika.org")
        driver.find_element(By.ID, "login-password").send_keys("WrongPassword999!")
        driver.find_element(By.ID, "login-submit-btn").click()
        time.sleep(1.0)

        # Check for alert dialog
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        self.assertTrue("ব্যর্থ" in alert_text or "সঠিক নয়" in alert_text or "অনুপস্থিত" in alert_text, f"Unexpected alert message: {alert_text}")

        # Modal should remain open
        auth_modal = driver.find_element(By.ID, "auth-modal")
        self.assertTrue(auth_modal.is_displayed())

    def test_11_citizen_denied_admin_route_enforcement(self):
        """Verify that citizen role is denied access to Admin backend API endpoints (403 Forbidden)."""
        driver = self.driver
        # Log in as Citizen
        driver.execute_script("openAuthModal('login');")
        time.sleep(0.3)
        driver.find_element(By.ID, "demo-login-citizen").click()
        time.sleep(1.5)

        # Make fetch request to admin-only endpoint
        status_code = driver.execute_async_script("""
            const callback = arguments[arguments.length - 1];
            fetch('/api/v1/admin/users', {
                headers: LandTechAPI.getHeaders()
            }).then(r => callback(r.status))
              .catch(e => callback(500));
        """)

        self.assertEqual(status_code, 403, f"Citizen must receive 403 Forbidden on admin endpoint, got {status_code}")

    def test_12_public_role_selector_removed(self):
        """Verify that public role selector (#app-role-select) is completely removed from the DOM."""
        driver = self.driver
        driver.get(BASE_URL)
        time.sleep(1)

        # Check for legacy role dropdown
        role_selects = driver.find_elements(By.ID, "app-role-select")
        self.assertEqual(len(role_selects), 0, "Public #app-role-select dropdown must NOT exist in the DOM")

        role_switch_boxes = driver.find_elements(By.CSS_SELECTOR, ".role-switch-box")
        self.assertEqual(len(role_switch_boxes), 0, "Public .role-switch-box container must NOT exist in the DOM")

    def test_13_role_nav_isolation_and_403_unauthorized_page(self):
        """Verify that Citizen sees only Citizen nav items, and navigating to unauthorized route renders 403 page."""
        driver = self.driver
        driver.execute_script("openAuthModal('login');")
        time.sleep(0.3)
        driver.find_element(By.ID, "demo-login-citizen").click()
        time.sleep(1.5)

        # Citizen should NOT see admin or officer navigation
        admin_users_nav = driver.find_elements(By.ID, "nav-item-users")
        self.assertEqual(len(admin_users_nav), 0, "Citizen must NOT have admin users navigation in sidebar")

        officer_cases_nav = driver.find_elements(By.ID, "nav-item-officer-cases")
        self.assertEqual(len(officer_cases_nav), 0, "Citizen must NOT have officer cases navigation in sidebar")

        # Attempt to forcibly switch to an unauthorized page via JavaScript
        driver.execute_script("switchAppPage('users');")
        time.sleep(0.5)

        # Page unauthorized (403 Access Denied) should be active
        unauthorized_page = driver.find_element(By.ID, "page-unauthorized")
        self.assertTrue(unauthorized_page.is_displayed(), "Unauthorized page should be visible for restricted route")
        self.assertIn("অননুমোদিত প্রবেশাধিকার", unauthorized_page.text)
        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "13_unauthorized_403_rendered.png"))

    def test_14_session_restoration_after_page_refresh(self):
        """Verify that refreshing the page restores the active session and preserves the role."""
        driver = self.driver
        driver.refresh()
        time.sleep(1.5)

        # After refresh, session must be restored from localStorage
        stored_user = driver.execute_script("return LandTechAPI.currentUser;")
        self.assertIsNotNone(stored_user, "Stored user should be restored")
        self.assertEqual(stored_user.get("role"), "CITIZEN", "Restored role must match CITIZEN")


if __name__ == '__main__':
    unittest.main()


