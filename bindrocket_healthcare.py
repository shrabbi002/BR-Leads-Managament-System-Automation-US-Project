"""
BindRocket HEALTHCARE Form Automation (ULTRA-FAST)
===================================================
Fills the Healthcare form using JavaScript injection.

Usage:
    python bindrocket_healthcare.py
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
from selenium.common.exceptions import TimeoutException
from faker import Faker

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL = "https://dev.bindrocket.com"
API_URL = "https://dev-api.bindrocket.com"
EMAIL = "sam201td@gmail.com"
PASSWORD = "Shrabbi1234@#"
fake = Faker("en_US")
SAVE_BTN_XPATH = "/html/body/div[1]/div[2]/div[2]/div/div[3]/form/div[2]/div/button"

logging.basicConfig(level=logging.INFO, format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("healthcare_automation_log.txt", mode="w", encoding="utf-8")])
log = logging.getLogger(__name__)
def p(msg):
    log.info(msg); sys.stdout.flush()


# ── Chrome Driver ─────────────────────────────────────────────────────────────
def create_driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--log-level=3")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)
    svc = Service(log_output=os.devnull)
    driver = webdriver.Chrome(options=opts, service=svc)
    driver.set_page_load_timeout(45)
    driver.implicitly_wait(1)
    return driver


# ── JS Helpers ────────────────────────────────────────────────────────────────

def js_set_by_name(driver, name, value, label=""):
    result = driver.execute_script("""
        var el = document.querySelector("input[name='" + arguments[0] + "']");
        if (!el) el = document.querySelector("textarea[name='" + arguments[0] + "']");
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
    """, name, str(value))
    if result == "OK":
        p(f"   ✅ {label}: {value}")
    else:
        p(f"   ⚠️ {label}: not found (name='{name}')")
    return result == "OK"


def js_set_by_placeholder(driver, placeholder, value, label=""):
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


def js_set_nth_date(driver, n, value, label=""):
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input');
        var dateFields = [];
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].placeholder === 'MM/DD/YYYY' && inputs[i].offsetParent) {
                dateFields.push(inputs[i]);
            }
        }
        if (arguments[0] >= dateFields.length) return 'NOT_FOUND:' + dateFields.length;
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
        p(f"   ⚠️ {label}: date#{n} ({result})")
    return result == "OK"


def js_click_radio_by_name(driver, name, idx=0):
    """Click nth radio button of a group (0-based)."""
    result = driver.execute_script("""
        var radios = document.querySelectorAll('input[type="radio"][name="' + arguments[0] + '"]');
        if (arguments[1] < radios.length) { radios[arguments[1]].click(); return 'OK'; }
        return radios.length > 0 ? 'ALREADY' : 'NOT_FOUND';
    """, name, idx)
    if result == "OK":
        p(f"   ✅ Radio [{name}]: option {idx} selected")
    return result == "OK"


def js_click_radio_by_label(driver, label_text, label=""):
    result = driver.execute_script("""
        var labels = document.querySelectorAll('label, span, div');
        for (var i = 0; i < labels.length; i++) {
            var t = labels[i].textContent.trim();
            if (t === arguments[0]) {
                var radio = labels[i].querySelector('input[type="radio"]');
                if (!radio) radio = labels[i].parentElement.querySelector('input[type="radio"]');
                if (!radio) {
                    var forAttr = labels[i].getAttribute('for');
                    if (forAttr) radio = document.getElementById(forAttr);
                }
                if (!radio) {
                    var prev = labels[i].previousElementSibling;
                    if (prev && prev.type === 'radio') radio = prev;
                }
                if (radio) { radio.click(); return 'OK'; }
            }
        }
        return 'NOT_FOUND';
    """, label_text)
    if result == "OK":
        p(f"   ✅ {label or label_text}: {label_text}")
    else:
        p(f"   ⚠️ {label or 'Radio'}: '{label_text}' not found")
    return result == "OK"


def js_check_all_checkboxes(driver):
    count = driver.execute_script("""
        var cbs = document.querySelectorAll('input[type="checkbox"]');
        var c = 0;
        for (var i = 0; i < cbs.length; i++) {
            if (cbs[i].offsetParent && !cbs[i].checked) { cbs[i].click(); c++; }
        }
        return c;
    """)
    if count:
        p(f"   ✅ Checkboxes: {count} checked")
    return count


def js_select_dropdown(driver, name_or_selector, option_idx=1):
    """Select an option from a native <select> dropdown by name."""
    result = driver.execute_script("""
        var sel = null;
        var sels = document.querySelectorAll('select');
        for (var i = 0; i < sels.length; i++) {
            if (sels[i].name === arguments[0]) { sel = sels[i]; break; }
        }
        if (!sel) {
            try { sel = document.querySelector(arguments[0]); } catch(e) {}
        }
        if (!sel) return 'NOT_FOUND';
        var opts = sel.options;
        if (arguments[1] < opts.length) {
            sel.selectedIndex = arguments[1];
            sel.dispatchEvent(new Event('change', {bubbles: true}));
            return opts[arguments[1]].text;
        }
        return 'NO_OPTIONS';
    """, name_or_selector, option_idx)
    if result and result not in ("NOT_FOUND", "NO_OPTIONS"):
        p(f"   ✅ Select [{name_or_selector}]: {result}")
    else:
        p(f"   ⚠️ Select [{name_or_selector}]: {result}")
    return result


def search_location(driver, field_idx, term, label):
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
            p(f"   ⚠️ {label}: no dropdown appeared")
        return selected is not None
    except Exception as e:
        p(f"   ⚠️ {label}: {e}")
        return False


# ── Data Generator ────────────────────────────────────────────────────────────

def gen_healthcare_data():
    """Generate random US-based data for Healthcare form."""
    fn, ln = fake.first_name(), fake.last_name()
    dob = fake.date_of_birth(minimum_age=21, maximum_age=65)

    us_states = ["Texas", "California", "Florida", "New York", "Ohio",
                 "Illinois", "Georgia", "Virginia", "Colorado", "Arizona",
                 "Michigan", "North Carolina", "Pennsylvania", "Washington"]

    dep_name = fake.first_name() + " " + ln
    dep_dob = fake.date_of_birth(minimum_age=1, maximum_age=18)
    dep_relations = ["Spouse", "Child", "Stepson or Stepdaughter", "Domestic Partner", "Other"]

    return {
        # Personal
        "first": fn, "last": ln, "full": f"{fn} {ln}",
        "email": f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@gmail.com",
        "phone": fake.numerify("(###) ###-####"),
        "work_phone": fake.numerify("(###) ###-####"),
        "dob": dob.strftime("%m/%d/%Y"),
        "addr_search": random.choice(us_states),
        # Income
        "income": str(random.randint(25000, 150000)),
        # Dependent
        "dep_name": dep_name,
        "dep_dob": dep_dob.strftime("%m/%d/%Y"),
        "dep_dob_iso": dep_dob.strftime("%Y-%m-%d"),  # For type=date input
        "dep_relation": random.choice(dep_relations),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    start = time.time()
    p("=" * 50)
    p("  BindRocket HEALTHCARE Form — ULTRA FAST")
    p(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p("=" * 50)

    # ── Step 1: API Login ─────────────────────────────────────────────────────
    p("\n🔐 Logging in...")
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

    # ── Step 2: Browser → Healthcare Form ─────────────────────────────────────
    p("\n🌐 Loading Healthcare form...")
    t0 = time.time()
    driver = create_driver()

    try:
        try:
            driver.get(f"{BASE_URL}/login")
        except TimeoutException:
            pass
        time.sleep(1)

        # Set cookies
        for k, v in {
            "token": token, "user_id": str(user["id"]),
            "firstname": user["firstname"].strip(), "lastname": user["lastname"].strip(),
            "email": user["email"], "role": user["role"],
            "external_user": str(user.get("external_user", False)).lower(),
            "agency_id": str(agency_id), "agent_id": agent_id,
            "seentour": str(user.get("is_first_login", False)).lower(),
            "authenticated": "true",
        }.items():
            try: driver.add_cookie({"name": k, "value": v, "path": "/"})
            except: pass

        # LocalStorage
        for key in ["billing", "package_info"]:
            driver.execute_script(f"localStorage.setItem('{key}', '{json.dumps(ld.get(key, {}))}');")
        driver.execute_script(f"localStorage.setItem('billing_addons', '{json.dumps(ld.get('billingAddons', []))}');")

        # Navigate to HEALTHCARE form
        form_url = f"{BASE_URL}/forms/healthcare?agency_id={agency_id}&agent_id={agent_id}"
        try:
            driver.get(form_url)
        except TimeoutException:
            p("   ⚠️ Page slow, continuing...")

        # Wait for form — with retry
        form_loaded = False
        for attempt in range(3):
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input")))
                field_count = driver.execute_script(
                    "return document.querySelectorAll('input').length;")
                if field_count and field_count > 3:
                    form_loaded = True
                    break
            except TimeoutException:
                pass
            if "login" in driver.current_url.lower():
                p("   ❌ TFA bypass failed"); return
            p(f"   ⚠️ Attempt {attempt+1}: Form not ready, retrying...")
            try:
                driver.refresh()
            except TimeoutException:
                pass
            time.sleep(3)

        if not form_loaded:
            time.sleep(5)
        p(f"   ✅ Form ready ({time.time()-t0:.1f}s)")

        # ── Diagnostic: Dump all form fields ──────────────────────────────────
        fields_info = driver.execute_script("""
            var inputs = document.querySelectorAll('input, select, textarea');
            var info = [];
            for (var i = 0; i < inputs.length; i++) {
                var el = inputs[i];
                if (!el.offsetParent && el.type !== 'hidden') continue;
                info.push({
                    idx: i, tag: el.tagName,
                    type: (el.type || ''), name: (el.name || ''),
                    id: (el.id || ''), ph: (el.placeholder || '')
                });
            }
            return info;
        """)
        if fields_info:
            p(f"\n   📊 Found {len(fields_info)} visible form fields:")
            for f in fields_info:
                p(f"   [{f['idx']}] <{f['tag'].lower()}> type={f['type']} name={f['name']} "
                  f"id={f['id']} ph=\"{f['ph']}\"")
        else:
            p("   ⚠️ No form fields found!")

        # ── Step 3: Generate data and fill ────────────────────────────────────
        d = gen_healthcare_data()
        p(f"\n📝 Filling Healthcare form...")
        p(f"   👤 {d['full']} | {d['email']} | {d['phone']}")
        p(f"   📅 DOB: {d['dob']} | Income: ${d['income']}")
        p(f"   👶 Dependent: {d['dep_name']} | Relation: {d['dep_relation']}")
        t0 = time.time()

        # ── Personal Information ──────────────────────────────────────────────
        p("\n   ─── Personal Information ───")
        js_set_by_placeholder(driver, "Client Lookup", d["full"], "Client Lookup")
        js_set_by_name(driver, "firstName", d["first"], "First Name")
        js_set_by_name(driver, "lastName", d["last"], "Last Name")
        js_set_by_name(driver, "emailAddress", d["email"], "Email")

        # Address — Google Places autocomplete
        search_location(driver, 0, d["addr_search"], "Address")

        js_set_by_name(driver, "mobileNumber", d["phone"], "Mobile")
        js_set_by_name(driver, "workNumber", d["work_phone"], "Work Phone")

        # DOB — only 1 MM/DD/YYYY date field on this form
        js_set_nth_date(driver, 0, d["dob"], "Date of Birth")

        # ── Radios ────────────────────────────────────────────────────────────
        p("\n   ─── Radios ───")
        # Gender: 0=Male, 1=Female
        gender_idx = random.choice([0, 1])
        js_click_radio_by_name(driver, "gender", gender_idx)
        # Tobacco: 0=Yes, 1=No
        tobacco_idx = random.choice([0, 1])
        js_click_radio_by_name(driver, "tobacoUsage", tobacco_idx)

        # ── Select Dropdowns ──────────────────────────────────────────────────
        p("\n   ─── Dropdowns ───")
        # Immigration Status dropdown
        js_select_dropdown(driver, "immigrantStatus", random.randint(1, 3))
        # Employment Status dropdown
        js_select_dropdown(driver, "employmentStatus", random.randint(1, 3))

        # ── Income ────────────────────────────────────────────────────────────
        p("\n   ─── Income ───")
        js_set_by_name(driver, "incomeAmount", d["income"], "Income Amount")

        # ── Dependent Information ─────────────────────────────────────────────
        p("\n   ─── Dependent ───")
        js_set_by_name(driver, "dependents.0.name", d["dep_name"], "Dependent Name")

        # Dependent DOB — type=date, needs YYYY-MM-DD format
        driver.execute_script("""
            var el = document.querySelector("input[name='dependents.0.dob']");
            if (el) {
                try {
                    var proto = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value');
                    if (proto && proto.set) proto.set.call(el, arguments[0]);
                    else el.value = arguments[0];
                } catch(e) { el.value = arguments[0]; }
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
            }
        """, d["dep_dob_iso"])
        p(f"   ✅ Dependent DOB: {d['dep_dob']}")

        # Dependent dropdowns
        js_select_dropdown(driver, "dependents.0.gender", random.randint(1, 2))
        js_select_dropdown(driver, "dependents.0.immigration", random.randint(1, 3))
        js_select_dropdown(driver, "dependents.0.relation", random.randint(1, 5))
        js_select_dropdown(driver, "dependents.0.tobacco", random.randint(1, 2))

        # ── Report remaining empty fields ─────────────────────────────────────
        remaining = driver.execute_script("""
            var inputs = document.querySelectorAll('input[type="text"], input[type="number"], input[type="email"]');
            var empty = [];
            for (var i = 0; i < inputs.length; i++) {
                if (inputs[i].offsetParent && !inputs[i].value && inputs[i].placeholder !== 'Client Lookup') {
                    empty.push({name: inputs[i].name || '', ph: inputs[i].placeholder || '', type: inputs[i].type || ''});
                }
            }
            return empty;
        """)
        if remaining:
            p(f"\n   📊 {len(remaining)} empty fields remaining:")
            for rf in remaining:
                p(f"      name={rf['name']} ph=\"{rf['ph']}\" type={rf['type']}")

        p(f"\n   ⚡ Form filled in {time.time()-t0:.1f}s")

        # ── Step 4: Save ──────────────────────────────────────────────────────
        p("\n💾 Saving...")
        time.sleep(0.5)
        try:
            save_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, SAVE_BTN_XPATH)))
            save_btn.click()
            p("   ✅ Save clicked!")
        except TimeoutException:
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
                p("   ✅ Save/Submit (JS fallback)")

        # ── Step 5: Lead Source modal ─────────────────────────────────────────
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
            p("📋 Lead Source modal...")
            sources = ["Call", "SMS", "Friend", "Web", "Third party", "Renewal"]
            chosen = random.choice(sources)

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
                var items = document.querySelectorAll('div, li, span');
                var options = ['Call', 'SMS', 'Friend', 'Web', 'Third party', 'Renewal'];
                for (var i = 0; i < items.length; i++) {{
                    var t = items[i].textContent.trim();
                    if (t === '{chosen}') {{ items[i].click(); return t; }}
                }}
                for (var i = 0; i < items.length; i++) {{
                    var t = items[i].textContent.trim();
                    if (options.indexOf(t) >= 0) {{ items[i].click(); return t; }}
                }}
                return null;
            """)
            p(f"   ✅ Lead Source: {selected or 'selected'}")
            time.sleep(0.5)

            driver.execute_script("""
                var btns = document.querySelectorAll('button');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.trim() === 'Save') { btns[i].click(); return; }
                }
            """)
            p("   ✅ Saved!")
            time.sleep(1)

        elapsed = time.time() - start
        p(f"\n{'=' * 50}")
        p(f"  ✅ Done in {elapsed:.1f}s")
        p(f"  📍 {driver.current_url}")
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
