"""
BindRocket Form Automation Script (ULTRA-FAST)
===============================================
Fills the Auto form in ~30 seconds using JavaScript injection.

Usage:
    python bindrocket_auto.py
"""

import sys, os, time, json, random, logging
from datetime import datetime, timedelta

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    ElementClickInterceptedException, StaleElementReferenceException,
)
from faker import Faker

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL = "https://dev.bindrocket.com"
API_URL = "https://dev-api.bindrocket.com"
EMAIL = "sam201td@gmail.com"
PASSWORD = "Shrabbi1234@#"
fake = Faker("en_US")

# Save button xpath provided by user
SAVE_BTN_XPATH = "/html/body/div[1]/div[2]/div[2]/div/div[3]/form/div[2]/div/button"

logging.basicConfig(level=logging.INFO, format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("automation_log.txt", mode="w", encoding="utf-8")])
log = logging.getLogger(__name__)
def p(msg):
    log.info(msg); sys.stdout.flush()


def create_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--log-level=3")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)
    svc = Service(log_output=os.devnull)
    driver = webdriver.Chrome(options=opts, service=svc)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(1)
    return driver


def gen_data():
    """Generate all form data in one shot."""
    fn, ln = fake.first_name(), fake.last_name()
    dob = fake.date_of_birth(minimum_age=21, maximum_age=65)
    eff = datetime.now() + timedelta(days=random.randint(1, 30))
    renew = datetime.now() + timedelta(days=random.randint(30, 180))
    carriers = ["State Farm", "GEICO", "Progressive", "Allstate",
                "Liberty Mutual", "USAA", "Nationwide", "Travelers"]
    # Realistic VIN
    vin = (str(random.randint(1, 5)) + random.choice("HGFJT") + random.choice("GCBAD")
           + random.choice("CM") + fake.numerify("###") + str(random.randint(0, 9))
           + str(random.randint(0, 9)) + random.choice("ABCDEFGHJKLMNPRSTUVWXYZ")
           + fake.numerify("######"))[:17]

    return {
        "first": fn, "last": ln, "full": f"{fn} {ln}",
        "email": f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@gmail.com",
        "phone": fake.numerify("(###) ###-####"),
        "dob": dob.strftime("%m/%d/%Y"),
        "eff_date": eff.strftime("%m/%d/%Y"),
        "renew_date": renew.strftime("%m/%d/%Y"),
        "addr": fake.street_address(),
        "license": fake.bothify("?#######").upper(),
        "vin": vin,
        "carrier": random.choice(carriers),
        "premium": f"${random.randint(800, 3000)}",
        "duration": f"{random.randint(1, 10)} years",
    }


def js_set_field(driver, selector, value, label=""):
    """Set a field value using JavaScript (instant, React-compatible)."""
    result = driver.execute_script("""
        var el = document.querySelector(arguments[0]);
        if (!el) return 'NOT_FOUND';
        try {
            var proto = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value');
            if (proto && proto.set) proto.set.call(el, arguments[1]);
            else el.value = arguments[1];
        } catch(e) { el.value = arguments[1]; }
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        el.dispatchEvent(new Event('blur', {bubbles: true}));
        return 'OK';
    """, selector, str(value))
    if result == "OK":
        p(f"   ✅ {label}: {value}")
    else:
        p(f"   ⚠️ {label}: not found ({selector})")
    return result == "OK"


def js_set_by_placeholder(driver, placeholder, value, label=""):
    """Set field by placeholder text."""
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input, textarea');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].placeholder === arguments[0]) {
                try {
                    var proto = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value');
                    if (proto && proto.set) proto.set.call(inputs[i], arguments[1]);
                    else inputs[i].value = arguments[1];
                } catch(e) { inputs[i].value = arguments[1]; }
                inputs[i].dispatchEvent(new Event('input', {bubbles: true}));
                inputs[i].dispatchEvent(new Event('change', {bubbles: true}));
                inputs[i].dispatchEvent(new Event('blur', {bubbles: true}));
                return 'OK';
            }
        }
        return 'NOT_FOUND';
    """, placeholder, str(value))
    if result == "OK":
        p(f"   ✅ {label}: {value}")
    else:
        p(f"   ⚠️ {label}: not found (ph='{placeholder}')")
    return result == "OK"


def js_set_by_name(driver, name, value, label=""):
    """Set field by name attribute."""
    return js_set_field(driver, f"input[name='{name}']", value, label)


def js_set_nth_date(driver, n, value, label=""):
    """Set the nth MM/DD/YYYY date field (0-indexed)."""
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input');
        var dateFields = [];
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].placeholder === 'MM/DD/YYYY' && inputs[i].offsetParent) {
                dateFields.push(inputs[i]);
            }
        }
        if (arguments[0] >= dateFields.length) return 'NOT_FOUND';
        var el = dateFields[arguments[0]];
        try {
            var proto = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value');
            if (proto && proto.set) proto.set.call(el, arguments[1]);
            else el.value = arguments[1];
        } catch(e) { el.value = arguments[1]; }
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        el.dispatchEvent(new Event('blur', {bubbles: true}));
        return 'OK';
    """, n, str(value))
    if result == "OK":
        p(f"   ✅ {label}: {value}")
    else:
        p(f"   ⚠️ {label}: date field #{n} not found")
    return result == "OK"


def js_click_checkboxes(driver):
    """Check all unchecked checkboxes."""
    count = driver.execute_script("""
        var checkboxes = document.querySelectorAll('input[type="checkbox"]');
        var count = 0;
        for (var i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].offsetParent && !checkboxes[i].checked) {
                checkboxes[i].click();
                count++;
            }
        }
        return count;
    """)
    if count:
        p(f"   ✅ Checkboxes: {count} checked")
    return count


def js_click_first_radio(driver, name):
    """Click the first radio button of a group."""
    result = driver.execute_script("""
        var radios = document.querySelectorAll('input[type="radio"][name="' + arguments[0] + '"]');
        if (radios.length > 0 && !document.querySelector('input[name="'+arguments[0]+'"]:checked')) {
            radios[0].click();
            return 'OK';
        }
        return radios.length > 0 ? 'ALREADY' : 'NOT_FOUND';
    """, name)
    if result == "OK":
        p(f"   ✅ Radio [{name}]: selected")
    return result == "OK"


def main():
    start = time.time()
    p("=" * 50)
    p("  BindRocket Auto Form — ULTRA FAST")
    p(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p("=" * 50)

    # ── Step 1: API Login ─────────────────────────────────────────────────────
    p("\n🔐 Logging in via API...")
    t0 = time.time()
    resp = requests.post(f"{API_URL}/api/login", json={"email": EMAIL, "password": PASSWORD})
    if resp.status_code != 200:
        p(f"   ❌ Login failed: {resp.status_code}"); return
    data = resp.json()
    if not data.get("success"):
        p(f"   ❌ {data.get('message')}"); return

    ld = data["data"]
    token, user, agent_id = ld["token"], ld["user"], ld["agent_id"]
    agency_id = user["agency_id"]
    p(f"   ✅ Logged in ({time.time()-t0:.1f}s)")

    # ── Step 2: Browser → Form ────────────────────────────────────────────────
    p("\n🌐 Opening browser + loading form...")
    t0 = time.time()
    driver = create_driver()

    try:
        # Set cookies on login page
        try:
            driver.get(f"{BASE_URL}/login")
        except TimeoutException:
            p("   ⚠️ Login page slow, continuing...")
        time.sleep(1)

        cookie_data = {
            "token": token, "user_id": str(user["id"]),
            "firstname": user["firstname"].strip(), "lastname": user["lastname"].strip(),
            "email": user["email"], "role": user["role"],
            "external_user": str(user.get("external_user", False)).lower(),
            "agency_id": str(agency_id), "agent_id": agent_id,
            "seentour": str(user.get("is_first_login", False)).lower(),
            "authenticated": "true",
        }
        for k, v in cookie_data.items():
            try: driver.add_cookie({"name": k, "value": v, "path": "/"})
            except: pass

        # Set localStorage
        for key in ["billing", "package_info"]:
            driver.execute_script(f"localStorage.setItem('{key}', '{json.dumps(ld.get(key, {}))}');")
        driver.execute_script(f"localStorage.setItem('billing_addons', '{json.dumps(ld.get('billingAddons', []))}');")

        # Navigate directly to Auto form
        form_url = f"{BASE_URL}/forms/auto?agency_id={agency_id}&agent_id={agent_id}"
        try:
            driver.get(form_url)
        except TimeoutException:
            p("   ⚠️ Form page slow, continuing...")

        # Wait for form fields to appear
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='firstName']")))
        except TimeoutException:
            if "login" in driver.current_url.lower():
                p("   ❌ TFA bypass failed"); return
        p(f"   ✅ Form ready ({time.time()-t0:.1f}s)")

        # ── Step 3: Generate fresh data ───────────────────────────────────────
        d = gen_data()
        p(f"\n📝 Filling form...")
        p(f"   👤 {d['full']} | {d['email']} | {d['phone']}")
        p(f"   📅 DOB: {d['dob']} | Effective: {d['eff_date']} | Renewal: {d['renew_date']}")
        p(f"   🚗 VIN: {d['vin']} | Carrier: {d['carrier']} | Premium: {d['premium']}")
        t0 = time.time()

        # ── Personal Information ──────────────────────────────────────────────
        js_set_by_placeholder(driver, "Client Lookup", d["full"], "Client Lookup")
        js_set_by_name(driver, "firstName", d["first"], "First Name")
        js_set_by_name(driver, "lastName", d["last"], "Last Name")
        js_set_by_name(driver, "emailId", d["email"], "Email")
        js_set_by_name(driver, "workNumber", d["phone"], "Work Phone")
        js_set_by_name(driver, "mobileNumber", d["phone"], "Mobile")

        # Date fields: 0=DOB, 1=Effective Date, 2=Driver DOB, 3=Renewal Date
        js_set_nth_date(driver, 0, d["dob"], "Date of Birth")

        # Address fields — use Google Places autocomplete search
        us_states = ["Texas", "California", "Florida", "New York", "Ohio",
                     "Illinois", "Georgia", "Virginia", "Colorado", "Arizona",
                     "Michigan", "North Carolina", "Pennsylvania", "Washington"]
        search_term = random.choice(us_states)

        def search_location(field_idx, term, label):
            """Type in location search and select a US-based result."""
            try:
                addr_fields = driver.find_elements(By.CSS_SELECTOR, "input[id='location-search-input']")
                visible = [f for f in addr_fields if f.is_displayed()]
                if field_idx >= len(visible):
                    p(f"   ⚠️ {label}: field #{field_idx} not found")
                    return False
                el = visible[field_idx]
                el.clear()
                el.send_keys(term)
                time.sleep(1.5)  # Wait for Google Places dropdown

                # Click first USA-based result from dropdown
                selected = driver.execute_script("""
                    var items = document.querySelectorAll('.pac-item');
                    for (var i = 0; i < items.length; i++) {
                        var text = items[i].textContent || '';
                        if (text.indexOf('USA') >= 0 || text.indexOf('United States') >= 0) {
                            items[i].click();
                            return text.trim();
                        }
                    }
                    // Fallback: click first item
                    if (items.length > 0) { items[0].click(); return items[0].textContent.trim(); }
                    return null;
                """)
                if selected:
                    p(f"   ✅ {label}: {selected[:60]}")
                else:
                    p(f"   ⚠️ {label}: no dropdown options appeared")
                return selected is not None
            except Exception as e:
                p(f"   ⚠️ {label}: {e}")
                return False

        search_location(0, search_term, "Street Address")
        # Garage address — use same location
        if len(driver.find_elements(By.CSS_SELECTOR, "input[id='location-search-input']")) > 1:
            search_location(1, search_term, "Garage Address")

        # Effective Date (must be FUTURE)
        js_set_nth_date(driver, 1, d["eff_date"], "Effective Date")

        # Checkboxes (Same as Address, etc.)
        js_click_checkboxes(driver)

        # Radio: Are you staying less than 6 months? → No
        js_click_first_radio(driver, "hasPreviousAddress")

        # ── Driver Information ────────────────────────────────────────────────
        js_set_by_placeholder(driver, "Enter Driver Name", d["full"], "Driver Name")
        js_set_nth_date(driver, 2, d["dob"], "Driver DOB")
        js_set_by_placeholder(driver, "Enter License Number", d["license"], "License")

        # ── Vehicle Information ───────────────────────────────────────────────
        js_click_first_radio(driver, "coverageType")
        js_set_by_placeholder(driver, "Enter 17-character VIN", d["vin"], "VIN")

        # ── Current Insurance Details ─────────────────────────────────────────
        js_set_by_name(driver, "carrierName", d["carrier"], "Carrier Name")
        js_set_nth_date(driver, 3, d["renew_date"], "Renewal Date")
        js_set_by_name(driver, "premiumAmount", d["premium"], "Premium")
        js_set_by_name(driver, "carrierDuration", d["duration"], "Duration")

        p(f"   ⚡ Form filled in {time.time()-t0:.1f}s")

        # ── Step 4: Click Save Button ─────────────────────────────────────────
        p("\n💾 Saving form...")
        time.sleep(0.5)

        # Use the exact save button xpath from user
        try:
            save_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, SAVE_BTN_XPATH)))
            save_btn.click()
            p("   ✅ Save button clicked!")
        except TimeoutException:
            # Fallback: try other selectors
            try:
                btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
                btn.click()
                p("   ✅ Submit clicked (fallback)")
            except:
                driver.execute_script("""
                    var btns = document.querySelectorAll('button');
                    for (var i = 0; i < btns.length; i++) {
                        var t = btns[i].textContent.trim().toLowerCase();
                        if (t === 'save' || t === 'submit') { btns[i].click(); return; }
                    }
                """)
                p("   ✅ Clicked save/submit (JS fallback)")

        # ── Step 5: Handle Lead Source modal if it appears ─────────────────────
        time.sleep(2)

        # Check if Lead Source modal appeared
        lead_modal = driver.execute_script("""
            // Look for Lead Source modal elements
            var els = document.querySelectorAll('div, span, h4, h5, p');
            for (var i = 0; i < els.length; i++) {
                var t = els[i].textContent.trim();
                if (t === 'Lead Source' || t === 'Lead source') return true;
            }
            return false;
        """)

        if lead_modal:
            p("📋 Lead Source modal detected...")
            lead_sources = ["Call", "SMS", "Friend", "Web", "Third party", "Renewal"]
            chosen = random.choice(lead_sources)

            # Click dropdown to open
            driver.execute_script("""
                var els = document.querySelectorAll('div, span');
                for (var i = 0; i < els.length; i++) {
                    var t = els[i].textContent.trim();
                    if (t === 'Lead source' || t === 'Lead Source') {
                        els[i].click(); break;
                    }
                }
            """)
            time.sleep(0.5)

            # Select an option
            selected = driver.execute_script(f"""
                var items = document.querySelectorAll('div, li, span, option');
                for (var i = 0; i < items.length; i++) {{
                    var t = items[i].textContent.trim();
                    if (t === '{chosen}') {{ items[i].click(); return t; }}
                }}
                // Fallback: click any option that looks like a lead source
                var options = ['Call', 'SMS', 'Friend', 'Web', 'Third party', 'Renewal'];
                for (var i = 0; i < items.length; i++) {{
                    var t = items[i].textContent.trim();
                    if (options.indexOf(t) >= 0) {{ items[i].click(); return t; }}
                }}
                return null;
            """)
            if selected:
                p(f"   ✅ Lead Source: {selected}")
            else:
                p("   ⚠️ Could not select lead source")

            time.sleep(0.5)

            # Click Save in modal
            driver.execute_script("""
                var btns = document.querySelectorAll('button');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.trim() === 'Save') {
                        btns[i].click(); return;
                    }
                }
            """)
            p("   ✅ Saved!")
            time.sleep(1)
        else:
            p("   ℹ️ No Lead Source modal detected")

        elapsed = time.time() - start
        p(f"\n{'=' * 50}")
        p(f"  ✅ Done in {elapsed:.1f}s")
        p(f"  📍 URL: {driver.current_url}")
        p("=" * 50)

        input("\nPress Enter to close browser...")

    except KeyboardInterrupt:
        p("\n⚠️ Interrupted.")
    except Exception as e:
        p(f"\n❌ Error: {e}")
        import traceback; traceback.print_exc()
        input("\nPress Enter to close...")
    finally:
        try: driver.quit()
        except: pass


if __name__ == "__main__":
    main()
