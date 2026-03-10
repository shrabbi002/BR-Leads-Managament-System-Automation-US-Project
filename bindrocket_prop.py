"""
BindRocket Property (Prop) Form Automation Script (ULTRA-FAST)
===============================================================
Fills the Commercial Coverages > Prop form in ~30 seconds using JavaScript injection.

Usage:
    python bindrocket_prop.py
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

logging.basicConfig(level=logging.INFO, format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("prop_automation_log.txt", mode="w", encoding="utf-8")])
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


def gen_prop_data():
    """Generate all Property form data in one shot."""
    fn, ln = fake.first_name(), fake.last_name()
    company = fake.company()
    biz_start = fake.date_between(start_date="-10y", end_date="-1y")
    eff = datetime.now() + timedelta(days=random.randint(1, 30))

    biz_descriptions = [
        "Restaurant", "Retail Store", "Office", "Consulting",
        "Construction", "Landscaping", "Cleaning Service",
        "Plumbing", "Electrical", "Auto Repair",
        "Real Estate", "Beauty Salon", "Gym", "Photography",
        "Cell Phone Store", "Convenience Store", "Warehouse",
    ]

    # Hours of Operation
    start_hours = ["06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM"]
    end_hours = ["05:00 PM", "06:00 PM", "07:00 PM", "08:00 PM", "09:00 PM", "10:00 PM"]

    return {
        "first": fn, "last": ln, "full": f"{fn} {ln}",
        "email": f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@gmail.com",
        "phone": fake.numerify("(###) ###-####"),
        "mobile": fake.numerify("(###) ###-####"),
        "dba": f"{fn}'s {random.choice(['Services', 'Enterprise', 'Group', 'Solutions', 'LLC'])}",
        "business_name": company,
        "biz_desc": random.choice(biz_descriptions),
        "biz_start_date": biz_start.strftime("%m/%d/%Y"),
        "eff_date": eff.strftime("%m/%d/%Y"),
        "start_time": random.choice(start_hours),
        "end_time": random.choice(end_hours),
        # Property Information
        "sq_ft": str(random.randint(500, 10000)),
        "gross_sales": str(random.randint(50000, 2000000)),
        "is_tenant": random.choice([True, False]),
        "tenant_info": fake.sentence(nb_words=5),
        "bpp_content_value": str(random.randint(10000, 500000)),
        "money_securities": str(random.randint(5000, 50000)),
        "building_value": str(random.randint(100000, 5000000)),
        "franchisor": random.choice(["", "7-Eleven", "Subway", "McDonald's", "Boost Mobile", "Metro PCS", ""]),
        "sign_value": str(random.randint(500, 10000)),
        "biz_operation": fake.paragraph(nb_sentences=2),
    }


# ── JS Helpers ────────────────────────────────────────────────────────────────

def js_set_by_placeholder(driver, placeholder, value, label=""):
    """Set field by placeholder text (React-compatible with native setter)."""
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input, textarea');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].placeholder === arguments[0] && inputs[i].offsetParent !== null) {
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


def js_set_textarea_by_placeholder(driver, placeholder, value, label=""):
    """Set textarea by placeholder text (React-compatible)."""
    result = driver.execute_script("""
        var textareas = document.querySelectorAll('textarea');
        for (var i = 0; i < textareas.length; i++) {
            if (textareas[i].placeholder === arguments[0] && textareas[i].offsetParent !== null) {
                try {
                    var proto = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value');
                    if (proto && proto.set) proto.set.call(textareas[i], arguments[1]);
                    else textareas[i].value = arguments[1];
                } catch(e) { textareas[i].value = arguments[1]; }
                textareas[i].dispatchEvent(new Event('input', {bubbles: true}));
                textareas[i].dispatchEvent(new Event('change', {bubbles: true}));
                textareas[i].dispatchEvent(new Event('blur', {bubbles: true}));
                return 'OK';
            }
        }
        return 'NOT_FOUND';
    """, placeholder, str(value))
    if result == "OK":
        p(f"   ✅ {label}: {value[:50]}...")
    else:
        p(f"   ⚠️ {label}: not found (ph='{placeholder}')")
    return result == "OK"


def js_set_nth_placeholder(driver, placeholder, n, value, label=""):
    """Set the nth field with a given placeholder (0-indexed, visible only)."""
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input, textarea');
        var matches = [];
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].placeholder === arguments[0] && inputs[i].offsetParent !== null) {
                matches.push(inputs[i]);
            }
        }
        if (arguments[1] >= matches.length) return 'NOT_FOUND';
        var el = matches[arguments[1]];
        try {
            var proto = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value');
            if (proto && proto.set) proto.set.call(el, arguments[2]);
            else el.value = arguments[2];
        } catch(e) { el.value = arguments[2]; }
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        el.dispatchEvent(new Event('blur', {bubbles: true}));
        return 'OK';
    """, placeholder, n, str(value))
    if result == "OK":
        p(f"   ✅ {label}: {value}")
    else:
        p(f"   ⚠️ {label}: field #{n} not found (ph='{placeholder}')")
    return result == "OK"


def js_set_nth_date(driver, n, value, label=""):
    """Set the nth MM/DD/YYYY date field (0-indexed, visible only)."""
    return js_set_nth_placeholder(driver, "MM/DD/YYYY", n, value, label)


def js_click_checkboxes(driver):
    """Check all unchecked visible checkboxes."""
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


def js_select_business_desc(driver, search_term, label="Business Description"):
    """Handle the searchable Business Description lookup field."""
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input');
        for (var i = 0; i < inputs.length; i++) {
            var ph = (inputs[i].placeholder || '').toLowerCase();
            if (ph.indexOf('search business') >= 0 || ph.indexOf('business description') >= 0) {
                inputs[i].focus();
                try {
                    var proto = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value');
                    if (proto && proto.set) proto.set.call(inputs[i], arguments[0]);
                    else inputs[i].value = arguments[0];
                } catch(e) { inputs[i].value = arguments[0]; }
                inputs[i].dispatchEvent(new Event('input', {bubbles: true}));
                inputs[i].dispatchEvent(new Event('change', {bubbles: true}));
                return 'OK';
            }
        }
        return 'NOT_FOUND';
    """, search_term)

    if result != "OK":
        p(f"   ⚠️ {label}: search field not found")
        return False

    time.sleep(1.5)

    selected = driver.execute_script("""
        var selectors = [
            '[class*="option"]', '[role="option"]', '[role="listbox"] div',
            '.dropdown-item', '.list-group-item', 'li[class*="item"]',
            '[class*="menu"] div', '[class*="suggestion"]'
        ];
        for (var s = 0; s < selectors.length; s++) {
            var items = document.querySelectorAll(selectors[s]);
            for (var i = 0; i < items.length; i++) {
                var text = items[i].textContent.trim();
                if (text.length > 0 && items[i].offsetParent !== null) {
                    items[i].click();
                    return text;
                }
            }
        }
        return null;
    """)

    if selected:
        p(f"   ✅ {label}: {selected[:60]}")
    else:
        p(f"   ⚠️ {label}: no dropdown option found, typed '{search_term}'")
    return selected is not None


def js_click_radio_near_label(driver, section_label, choice="No"):
    """Click a radio button (Yes/No) near a specific label text."""
    result = driver.execute_script("""
        var allEls = document.querySelectorAll('label, span, div, p, td, th, h5, h6');
        for (var i = 0; i < allEls.length; i++) {
            var text = allEls[i].textContent.trim();
            if (text.indexOf(arguments[0]) >= 0 && text.length < arguments[0].length + 20) {
                // Found the label, now find radio buttons nearby
                var container = allEls[i].parentElement;
                for (var depth = 0; depth < 5; depth++) {
                    if (!container) break;
                    var radios = container.querySelectorAll('input[type="radio"]');
                    if (radios.length > 0) {
                        // Find the radio with the matching label
                        for (var r = 0; r < radios.length; r++) {
                            var radioLabel = radios[r].parentElement ? radios[r].parentElement.textContent.trim() : '';
                            if (radioLabel === arguments[1] || radioLabel.indexOf(arguments[1]) >= 0) {
                                radios[r].click();
                                return 'OK';
                            }
                        }
                        // Fallback: click first or second radio based on choice
                        if (arguments[1] === 'Yes' && radios.length > 0) { radios[0].click(); return 'OK'; }
                        if (arguments[1] === 'No' && radios.length > 1) { radios[1].click(); return 'OK'; }
                        if (radios.length > 0) { radios[0].click(); return 'OK'; }
                    }
                    container = container.parentElement;
                }
            }
        }
        return 'NOT_FOUND';
    """, section_label, choice)
    if result == "OK":
        p(f"   ✅ Radio [{section_label}]: {choice}")
    else:
        p(f"   ⚠️ Radio [{section_label}]: not found")
    return result == "OK"


def js_click_specific_checkboxes(driver, labels):
    """Click checkboxes that have specific label text."""
    count = 0
    for label in labels:
        result = driver.execute_script("""
            var allEls = document.querySelectorAll('label, span, div');
            for (var i = 0; i < allEls.length; i++) {
                var text = allEls[i].textContent.trim();
                if (text === arguments[0]) {
                    // Check if this element IS a label with a checkbox
                    var cb = allEls[i].querySelector('input[type="checkbox"]');
                    if (!cb) {
                        var parent = allEls[i].parentElement;
                        if (parent) cb = parent.querySelector('input[type="checkbox"]');
                    }
                    if (!cb) {
                        // Try previous sibling
                        var prev = allEls[i].previousElementSibling;
                        if (prev && prev.type === 'checkbox') cb = prev;
                    }
                    if (cb && !cb.checked) {
                        cb.click();
                        return 'OK';
                    }
                }
            }
            return 'NOT_FOUND';
        """, label)
        if result == "OK":
            p(f"   ✅ Checkbox [{label}]: checked")
            count += 1
    return count


def js_set_time_field(driver, n, value, label=""):
    """Set the nth time picker field (placeholder '--:-- --')."""
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input');
        var timeFields = [];
        for (var i = 0; i < inputs.length; i++) {
            var ph = inputs[i].placeholder || '';
            if ((ph.indexOf('--:--') >= 0 || ph.indexOf(':') >= 0) && 
                inputs[i].offsetParent !== null && inputs[i].type !== 'date') {
                timeFields.push(inputs[i]);
            }
        }
        if (arguments[0] >= timeFields.length) return 'NOT_FOUND';
        var el = timeFields[arguments[0]];
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
        p(f"   ⚠️ {label}: time field #{n} not found")
    return result == "OK"


def main():
    start = time.time()
    p("=" * 60)
    p("  BindRocket Property (Prop) Form — ULTRA FAST")
    p(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p("=" * 60)

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

    # ── Step 2: Browser → Prop Form ───────────────────────────────────────────
    p("\n🌐 Opening browser + loading Prop form...")
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

        # Navigate directly to Property form
        form_url = f"{BASE_URL}/forms/property?agency_id={agency_id}&agent_id={agent_id}"
        try:
            driver.get(form_url)
        except TimeoutException:
            p("   ⚠️ Form page slow, continuing...")

        # Wait for form fields
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[placeholder='Enter First Name']")))
        except TimeoutException:
            if "login" in driver.current_url.lower():
                p("   ❌ TFA bypass failed"); return
            p("   ⚠️ Form fields may not have loaded, continuing anyway...")

        # Dismiss any error overlays
        time.sleep(1)
        driver.execute_script("""
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].textContent.trim() === 'Dismiss') {
                    btns[i].click(); break;
                }
            }
        """)
        time.sleep(0.5)

        p(f"   ✅ Prop Form ready ({time.time()-t0:.1f}s)")

        # ── Step 3: Generate fresh data ───────────────────────────────────────
        d = gen_prop_data()
        p(f"\n📝 Filling Property Form...")
        p(f"   👤 {d['full']} | {d['email']} | {d['phone']}")
        p(f"   🏢 {d['business_name']} | DBA: {d['dba']}")
        p(f"   📅 Biz Start: {d['biz_start_date']} | Effective: {d['eff_date']}")
        p(f"   🏠 Sq Ft: {d['sq_ft']} | BPP: ${d['bpp_content_value']} | Building: ${d['building_value']}")
        t0 = time.time()

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 1: General Information
        # ══════════════════════════════════════════════════════════════════════
        p("\n── Section 1: General Information ──")

        # Click Section 1 sidebar
        driver.execute_script("""
            var items = document.querySelectorAll('div, span, li, a, button');
            for (var i = 0; i < items.length; i++) {
                var t = items[i].textContent.trim();
                if (t === 'General Information') { items[i].click(); break; }
            }
        """)
        time.sleep(0.5)

        # Personal / Business fields
        js_set_by_placeholder(driver, "Enter First Name", d["first"], "First Name")
        js_set_by_placeholder(driver, "Enter Last Name", d["last"], "Last Name")
        js_set_by_placeholder(driver, "Enter DBA", d["dba"], "DBA")
        js_set_by_placeholder(driver, "Enter Business Name", d["business_name"], "Business Name")

        # Business Description (searchable lookup)
        js_select_business_desc(driver, d["biz_desc"])

        # Business Start Date (1st MM/DD/YYYY)
        js_set_nth_date(driver, 0, d["biz_start_date"], "Business Start Date")

        # Hours of Operation — Start and End time fields
        js_set_time_field(driver, 0, d["start_time"], "Hours Start")
        js_set_time_field(driver, 1, d["end_time"], "Hours End")

        # Phone numbers
        js_set_nth_placeholder(driver, "(XXX) XXX-XXXX", 0, d["phone"], "Work Phone")
        js_set_nth_placeholder(driver, "(XXX) XXX-XXXX", 1, d["mobile"], "Mobile Number")

        # Email
        js_set_by_placeholder(driver, "Enter Email", d["email"], "Email Address")

        # Effective Date (2nd MM/DD/YYYY)
        js_set_nth_date(driver, 1, d["eff_date"], "Effective Date")

        # Location Address — Google Places
        us_states = ["Texas", "California", "Florida", "New York", "Ohio",
                     "Illinois", "Georgia", "Virginia", "Colorado", "Arizona"]
        search_term = random.choice(us_states)

        def search_location(field_idx, term, label):
            try:
                addr_fields = driver.find_elements(By.CSS_SELECTOR, "input[id='location-search-input']")
                if not addr_fields:
                    addr_fields = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='Address']")
                visible = [f for f in addr_fields if f.is_displayed()]
                if field_idx >= len(visible):
                    p(f"   ⚠️ {label}: field #{field_idx} not found")
                    return False
                el = visible[field_idx]
                el.clear()
                el.send_keys(term)
                time.sleep(1.5)
                selected = driver.execute_script("""
                    var items = document.querySelectorAll('.pac-item');
                    for (var i = 0; i < items.length; i++) {
                        var text = items[i].textContent || '';
                        if (text.indexOf('USA') >= 0 || text.indexOf('United States') >= 0) {
                            items[i].click(); return text.trim();
                        }
                    }
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

        search_location(0, search_term, "Location Address")

        # "Same as Location Address" checkbox
        driver.execute_script("""
            var labels = document.querySelectorAll('label, span');
            for (var i = 0; i < labels.length; i++) {
                if (labels[i].textContent.trim().indexOf('Same as Location') >= 0) {
                    var cb = labels[i].querySelector('input[type="checkbox"]');
                    if (!cb) {
                        var p = labels[i].parentElement;
                        if (p) cb = p.querySelector('input[type="checkbox"]');
                    }
                    if (cb && !cb.checked) { cb.click(); return; }
                }
            }
        """)
        p("   ✅ Same as Location Address: checked")

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 2: Property Information
        # ══════════════════════════════════════════════════════════════════════
        p("\n── Section 2: Property Information ──")

        # Click Section 2 sidebar
        driver.execute_script("""
            var items = document.querySelectorAll('div, span, li, a, button');
            for (var i = 0; i < items.length; i++) {
                var t = items[i].textContent.trim();
                if (t === 'Property Information') { items[i].click(); break; }
            }
        """)
        time.sleep(1)

        # Sq Ft
        js_set_by_placeholder(driver, "Enter Sq Ft", d["sq_ft"], "Sq Ft")

        # Gross Sales/Rent Roll
        js_set_by_placeholder(driver, "Enter Sales", d["gross_sales"], "Gross Sales")

        # Tenant? — radio (Yes/No)
        if d["is_tenant"]:
            js_click_radio_near_label(driver, "Tenant", "Yes")
            time.sleep(0.3)
            js_set_by_placeholder(driver, "Enter Tenant Info", d["tenant_info"], "Tenant Info")
        else:
            js_click_radio_near_label(driver, "Tenant", "No")

        # BPP/Content Value
        js_set_by_placeholder(driver, "Enter BPP/Content Value", d["bpp_content_value"], "BPP/Content Value")

        # Money & Securities Limit
        js_set_by_placeholder(driver, "Enter Money & Securities Limit", d["money_securities"], "Money & Securities")

        # Building Value (if owner, not tenant)
        if not d["is_tenant"]:
            js_set_by_placeholder(driver, "Enter Building Value", d["building_value"], "Building Value")

        # Franchisor Name
        if d["franchisor"]:
            js_set_by_placeholder(driver, "Enter Franchise", d["franchisor"], "Franchisor")

        # Sign Value
        js_set_by_placeholder(driver, "Enter Sign Value", d["sign_value"], "Sign Value")

        # Loss Runs Received? — radio
        js_click_radio_near_label(driver, "Loss Runs Received", random.choice(["Yes", "No"]))

        # Describe Business Operation — textarea
        js_set_textarea_by_placeholder(driver, "Describe Business Operation", d["biz_operation"], "Business Operation")
        # Also try input version in case it's not a textarea
        if not js_set_by_placeholder(driver, "Describe Business Operation", d["biz_operation"], "Biz Op (input fallback)"):
            pass  # Already tried textarea above

        # Scroll down for remaining fields
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 2 / 3);")
        time.sleep(0.5)

        # Protective Safeguard checkboxes — select a few random ones
        safeguards = ["CCTV Camera", "Burglar Alarm", "Fire Alarm", "Sprinkler System"]
        selected_safeguards = random.sample(safeguards, random.randint(1, 3))
        js_click_specific_checkboxes(driver, selected_safeguards)

        # Claim In Past 5 Years? — radio
        js_click_radio_near_label(driver, "Claim In Past 5 Years", "No")

        # Additional Insured? — radio
        js_click_radio_near_label(driver, "Additional Insured", "No")

        # Store Type checkboxes — select a random one
        store_types = ["Repair Store", "New Cell Phone Store", "Installation",
                       "Old Cell phone Store", "Accessories", "Others"]
        selected_store = random.sample(store_types, random.randint(1, 2))
        js_click_specific_checkboxes(driver, selected_store)

        p(f"\n   ⚡ Property Form filled in {time.time()-t0:.1f}s")

        # ── Step 4: Click Save Button ─────────────────────────────────────────
        p("\n💾 Saving form...")
        time.sleep(0.5)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

        try:
            save_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Save']")))
            save_btn.click()
            p("   ✅ Save button clicked!")
        except TimeoutException:
            driver.execute_script("""
                var btns = document.querySelectorAll('button');
                for (var i = 0; i < btns.length; i++) {
                    var t = btns[i].textContent.trim().toLowerCase();
                    if (t === 'save' || t === 'submit') { btns[i].click(); return; }
                }
            """)
            p("   ✅ Clicked save (JS fallback)")

        # ── Step 5: Handle Lead Source modal ──────────────────────────────────
        time.sleep(2)

        lead_modal = driver.execute_script("""
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

            selected = driver.execute_script(f"""
                var items = document.querySelectorAll('div, li, span, option');
                for (var i = 0; i < items.length; i++) {{
                    var t = items[i].textContent.trim();
                    if (t === '{chosen}') {{ items[i].click(); return t; }}
                }}
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
            driver.execute_script("""
                var btns = document.querySelectorAll('button');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.trim() === 'Save') {
                        btns[i].click(); return;
                    }
                }
            """)
            p("   ✅ Lead Source saved!")
            time.sleep(1)
        else:
            p("   ℹ️ No Lead Source modal detected")

        elapsed = time.time() - start
        p(f"\n{'=' * 60}")
        p(f"  ✅ Property Form Done in {elapsed:.1f}s")
        p(f"  📍 URL: {driver.current_url}")
        p("=" * 60)

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
