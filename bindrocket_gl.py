"""
BindRocket GL (General Liability) Form Automation Script (ULTRA-FAST)
=====================================================================
Fills the Commercial Coverages > GL form in ~30 seconds using JavaScript injection.

Usage:
    python bindrocket_gl.py
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
              logging.FileHandler("gl_automation_log.txt", mode="w", encoding="utf-8")])
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


def gen_gl_data():
    """Generate all GL form data in one shot."""
    fn, ln = fake.first_name(), fake.last_name()
    company = fake.company()
    biz_start = fake.date_between(start_date="-10y", end_date="-1y")
    eff = datetime.now() + timedelta(days=random.randint(1, 30))

    biz_descriptions = [
        "Restaurant", "Retail Store", "Office", "Consulting",
        "Construction", "Landscaping", "Cleaning Service",
        "Plumbing", "Electrical", "Auto Repair",
        "Real Estate", "Beauty Salon", "Gym", "Photography",
    ]

    gen_agg_options = ["1000000", "2000000", "3000000", "4000000", "5000000"]
    prod_agg_options = ["1000000", "2000000", "3000000"]
    each_occ_options = ["500000", "1000000", "2000000"]
    damage_prem_options = ["50000", "100000", "300000", "500000"]
    med_exp_options = ["5000", "10000", "15000"]
    pers_adv_options = ["500000", "1000000", "2000000"]
    deductible_options = ["500", "1000", "2500", "5000"]

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
        # GL Limits
        "gen_aggregate": random.choice(gen_agg_options),
        "prod_aggregate": random.choice(prod_agg_options),
        "pers_adv_injury": random.choice(pers_adv_options),
        "each_occurrence": random.choice(each_occ_options),
        "damage_premises": random.choice(damage_prem_options),
        "med_expense": random.choice(med_exp_options),
        "deductible": random.choice(deductible_options),
        # Business metrics
        "premium_amount": str(random.randint(1000, 10000)),
        "payroll": str(random.randint(50000, 500000)),
        "tiv": str(random.randint(100000, 2000000)),
        "num_employees": str(random.randint(1, 100)),
        "annual_sales": str(random.randint(100000, 5000000)),
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

    # Click the first matching dropdown option
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


def js_click_checkbox_near_label(driver, label_text):
    """Click a checkbox that is near a specific label text."""
    result = driver.execute_script("""
        // Strategy 1: Find labels/spans with text, then find nearby checkbox
        var allEls = document.querySelectorAll('label, span, div, p, td, th');
        for (var i = 0; i < allEls.length; i++) {
            // Check direct text content (not children's text)
            var directText = '';
            for (var j = 0; j < allEls[i].childNodes.length; j++) {
                if (allEls[i].childNodes[j].nodeType === 3) {
                    directText += allEls[i].childNodes[j].textContent;
                }
            }
            if (!directText.trim()) directText = allEls[i].textContent.trim();
            
            if (directText.trim() === arguments[0] || directText.trim().indexOf(arguments[0]) >= 0) {
                // Search in parent chain for checkbox
                var el = allEls[i];
                for (var depth = 0; depth < 5; depth++) {
                    var cb = el.querySelector('input[type="checkbox"]');
                    if (cb && !cb.checked) {
                        cb.click();
                        return 'OK';
                    }
                    el = el.parentElement;
                    if (!el) break;
                }
            }
        }
        return 'NOT_FOUND';
    """, label_text)
    if result == "OK":
        p(f"   ✅ Checkbox [{label_text}]: checked")
    else:
        p(f"   ⚠️ Checkbox [{label_text}]: not found")
    return result == "OK"


def js_set_nth_amount(driver, n, value, label=""):
    """Set the nth 'Enter amount' field (0-indexed, visible only)."""
    return js_set_nth_placeholder(driver, "Enter amount", n, value, label)


def main():
    start = time.time()
    p("=" * 60)
    p("  BindRocket GL (General Liability) Form — ULTRA FAST")
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

    # ── Step 2: Browser → GL Form ─────────────────────────────────────────────
    p("\n🌐 Opening browser + loading GL form...")
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

        # Navigate directly to GL form (fresh new form — no lead_id)
        form_url = f"{BASE_URL}/forms/general_liability?agency_id={agency_id}&agent_id={agent_id}"
        try:
            driver.get(form_url)
        except TimeoutException:
            p("   ⚠️ Form page slow, continuing...")

        # Wait for GL form fields — use placeholder-based selector
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

        p(f"   ✅ GL Form ready ({time.time()-t0:.1f}s)")

        # ── Step 3: Generate fresh data ───────────────────────────────────────
        d = gen_gl_data()
        p(f"\n📝 Filling GL Form...")
        p(f"   👤 {d['full']} | {d['email']} | {d['phone']}")
        p(f"   🏢 {d['business_name']} | DBA: {d['dba']}")
        p(f"   📅 Biz Start: {d['biz_start_date']} | Effective: {d['eff_date']}")
        p(f"   🛡️ Gen Agg: ${d['gen_aggregate']} | Each Occ: ${d['each_occurrence']}")
        t0 = time.time()

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 1: General Information
        # ══════════════════════════════════════════════════════════════════════
        p("\n── Section 1: General Information ──")

        # Click Section 1 sidebar item to ensure it's active
        driver.execute_script("""
            var items = document.querySelectorAll('div, span, li, a, button');
            for (var i = 0; i < items.length; i++) {
                var t = items[i].textContent.trim();
                if (t === 'General Information') { items[i].click(); break; }
            }
        """)
        time.sleep(0.5)

        # Personal / Business fields (using PLACEHOLDER selectors)
        js_set_by_placeholder(driver, "Enter First Name", d["first"], "First Name")
        js_set_by_placeholder(driver, "Enter Last Name", d["last"], "Last Name")
        js_set_by_placeholder(driver, "Enter DBA", d["dba"], "DBA")
        js_set_by_placeholder(driver, "Enter Business Name", d["business_name"], "Business Name")

        # Business Description (searchable lookup)
        js_select_business_desc(driver, d["biz_desc"])

        # Business Start Date (1st MM/DD/YYYY date field)
        js_set_nth_date(driver, 0, d["biz_start_date"], "Business Start Date")

        # Phone numbers (1st and 2nd (XXX) XXX-XXXX fields)
        js_set_nth_placeholder(driver, "(XXX) XXX-XXXX", 0, d["phone"], "Work Phone")
        js_set_nth_placeholder(driver, "(XXX) XXX-XXXX", 1, d["mobile"], "Mobile Number")

        # Email
        js_set_by_placeholder(driver, "Enter Email", d["email"], "Email Address")

        # Effective Date (2nd MM/DD/YYYY date field)
        js_set_nth_date(driver, 1, d["eff_date"], "Effective Date")

        # Location Address — Google Places autocomplete
        us_states = ["Texas", "California", "Florida", "New York", "Ohio",
                     "Illinois", "Georgia", "Virginia", "Colorado", "Arizona"]
        search_term = random.choice(us_states)

        def search_location(field_idx, term, label):
            """Type in location search and select a US-based result."""
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
                            items[i].click();
                            return text.trim();
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
        js_click_checkboxes(driver)

        # If mailing address still visible, fill it too
        time.sleep(0.5)
        mailing_fields = driver.find_elements(By.CSS_SELECTOR, "input[id='location-search-input']")
        if not mailing_fields:
            mailing_fields = driver.find_elements(By.CSS_SELECTOR, "input[placeholder='Address']")
        visible_mailing = [f for f in mailing_fields if f.is_displayed()]
        if len(visible_mailing) > 1:
            search_location(1, search_term, "Mailing Address")

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 2: General Liability & Limit
        # ══════════════════════════════════════════════════════════════════════
        p("\n── Section 2: General Liability & Limit ──")

        # Click Section 2 sidebar item
        driver.execute_script("""
            var items = document.querySelectorAll('div, span, li, a, button');
            for (var i = 0; i < items.length; i++) {
                var t = items[i].textContent.trim();
                if (t === 'General Liability & Limit' || t === 'General Liability & Limits') {
                    items[i].click(); break;
                }
            }
        """)
        time.sleep(1)

        # Scroll down to make Section 2 fields visible
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
        time.sleep(0.5)

        # GL Limit fields
        js_set_by_placeholder(driver, "Enter General Aggregate", d["gen_aggregate"], "General Aggregate")
        js_set_by_placeholder(driver, "Enter Products & Completed Operations Aggregate", d["prod_aggregate"], "Products & Comp Ops Aggregate")
        js_set_by_placeholder(driver, "Enter Personal & Advertising Injury", d["pers_adv_injury"], "Personal & Adv Injury")
        js_set_by_placeholder(driver, "Enter Each Occurrence", d["each_occurrence"], "Each Occurrence")
        js_set_by_placeholder(driver, "Enter Damage To Premises Rented To You", d["damage_premises"], "Damage to Premises")
        js_set_by_placeholder(driver, "Enter Medical Expense", d["med_expense"], "Medical Expense")
        js_set_by_placeholder(driver, "Enter Other Coverage, Restrictions, and/or Endorsements",
                              "Standard GL coverage", "Other Coverage/Endorsements")
        js_set_by_placeholder(driver, "Enter Deductible", d["deductible"], "Deductible")

        # Business Type Metrics — check checkbox then fill amount
        # Premium Amount
        js_click_checkbox_near_label(driver, "Premium Amount")
        time.sleep(0.3)
        js_set_nth_amount(driver, 0, d["premium_amount"], "Premium Amount")

        # Payroll
        js_click_checkbox_near_label(driver, "Payroll")
        time.sleep(0.3)
        js_set_nth_amount(driver, 1, d["payroll"], "Payroll")

        # TIV
        js_click_checkbox_near_label(driver, "TIV")
        time.sleep(0.3)
        js_set_nth_amount(driver, 2, d["tiv"], "TIV")

        # Scroll down for remaining fields
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 2 / 3);")
        time.sleep(0.5)

        # Number of Employees
        js_set_by_placeholder(driver, "Enter Number Of Employees", d["num_employees"], "Number of Employees")

        # Annual Sales
        js_set_by_placeholder(driver, "Enter Annual Sales", d["annual_sales"], "Annual Sales")

        p(f"\n   ⚡ GL Form filled in {time.time()-t0:.1f}s")

        # ── Step 4: Click Save Button ─────────────────────────────────────────
        p("\n💾 Saving form...")
        time.sleep(0.5)

        # Scroll to bottom to find Save button
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
        p(f"  ✅ GL Form Done in {elapsed:.1f}s")
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
