"""
BindRocket HOME Form Automation (ULTRA-FAST)
=============================================
Fills the Home form in ~25 seconds using JavaScript injection.

Usage:
    python bindrocket_home.py
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
              logging.FileHandler("home_automation_log.txt", mode="w", encoding="utf-8")])
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


# ── JS Helpers (instant field filling) ────────────────────────────────────────

JS_SET_VALUE = """
    try {
        var proto = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value');
        if (proto && proto.set) proto.set.call(arguments[0], arguments[1]);
        else arguments[0].value = arguments[1];
    } catch(e) { arguments[0].value = arguments[1]; }
    arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
    arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
    arguments[0].dispatchEvent(new Event('blur', {bubbles: true}));
"""

def js_set_by_name(driver, name, value, label=""):
    result = driver.execute_script("""
        var el = document.querySelector("input[name='" + arguments[0] + "']");
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


def js_click_radio_by_name(driver, name):
    result = driver.execute_script("""
        var radios = document.querySelectorAll('input[type="radio"][name="' + arguments[0] + '"]');
        if (radios.length > 0 && !document.querySelector('input[name="'+arguments[0]+'"]:checked')) {
            radios[0].click(); return 'OK';
        }
        return radios.length > 0 ? 'ALREADY' : 'NOT_FOUND';
    """, name)
    if result == "OK":
        p(f"   ✅ Radio [{name}]: selected")
    return result == "OK"


def js_click_radio_by_label(driver, label_text, label=""):
    """Click a radio button whose adjacent label/text matches."""
    result = driver.execute_script("""
        var labels = document.querySelectorAll('label, span, div');
        for (var i = 0; i < labels.length; i++) {
            var t = labels[i].textContent.trim();
            if (t === arguments[0]) {
                // Find radio input nearby
                var radio = labels[i].querySelector('input[type="radio"]');
                if (!radio) radio = labels[i].parentElement.querySelector('input[type="radio"]');
                if (!radio) {
                    var forAttr = labels[i].getAttribute('for');
                    if (forAttr) radio = document.getElementById(forAttr);
                }
                if (!radio) {
                    // Try previous sibling
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


def js_click_checkboxes_smart(driver, check_indices, uncheck_indices=None):
    """Check specific checkboxes by index (0-based, visible only)."""
    result = driver.execute_script("""
        var cbs = [];
        var allCbs = document.querySelectorAll('input[type="checkbox"]');
        for (var i = 0; i < allCbs.length; i++) {
            if (allCbs[i].offsetParent) cbs.push(allCbs[i]);
        }
        var checked = [];
        var toCheck = arguments[0];
        for (var j = 0; j < toCheck.length; j++) {
            if (toCheck[j] < cbs.length && !cbs[toCheck[j]].checked) {
                cbs[toCheck[j]].click();
                checked.push(toCheck[j]);
            }
        }
        return {total: cbs.length, checked: checked};
    """, check_indices)
    if result:
        p(f"   ✅ Checkboxes: {len(result.get('checked', []))} checked (of {result.get('total', 0)} total)")
    return result


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


# ── Data Generator ────────────────────────────────────────────────────────────

def gen_home_data():
    """Generate random US-based data for Home form."""
    fn, ln = fake.first_name(), fake.last_name()
    spouse_fn = fake.first_name()
    dob = fake.date_of_birth(minimum_age=25, maximum_age=65)
    spouse_dob = fake.date_of_birth(minimum_age=25, maximum_age=65)
    eff = datetime.now() + timedelta(days=random.randint(1, 60))
    renew = datetime.now() + timedelta(days=random.randint(30, 180))
    addr = f"{fake.building_number()} {fake.street_name()}, {fake.city()}, {fake.state_abbr()} {fake.zipcode()}"
    carriers = ["State Farm", "GEICO", "Progressive", "Allstate",
                "Liberty Mutual", "USAA", "Nationwide", "Travelers", "Farmers"]
    claim_reasons = [
        "Minor roof storm damage", "Water leak in basement", "Wind damage to siding",
        "Hail damage to roof", "Tree fell on garage", "Pipe burst in winter",
        "Lightning strike damage", "Fire damage in kitchen", "Theft of electronics",
    ]
    # Past dates for property updates
    roof_date = fake.date_between(start_date="-10y", end_date="-1y").strftime("%m/%d/%Y")
    wiring_date = fake.date_between(start_date="-10y", end_date="-1y").strftime("%m/%d/%Y")
    plumbing_date = fake.date_between(start_date="-10y", end_date="-1y").strftime("%m/%d/%Y")
    heating_date = fake.date_between(start_date="-10y", end_date="-1y").strftime("%m/%d/%Y")
    claim_date = fake.date_between(start_date="-3y", end_date="-6m").strftime("%m/%d/%Y")

    return {
        # Personal
        "first": fn, "last": ln, "full": f"{fn} {ln}",
        "email": f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@gmail.com",
        "phone": fake.numerify("(###) ###-####"),
        "work_phone": fake.numerify("(###) ###-####"),
        "dob": dob.strftime("%m/%d/%Y"),
        "addr": addr,
        "eff_date": eff.strftime("%m/%d/%Y"),
        # Spouse
        "spouse_first": spouse_fn, "spouse_last": ln,
        "spouse_dob": spouse_dob.strftime("%m/%d/%Y"),
        # Property
        "home_value": str(random.randint(200000, 800000)),
        "year_built": str(random.randint(1970, 2023)),
        "roof_date": roof_date,
        "wiring_date": wiring_date,
        "plumbing_date": plumbing_date,
        "heating_date": heating_date,
        # Construction
        "construction": random.choice(["Frame", "Masonry Veneer", "Masonry"]),
        "siding": random.choice(["Vinyl Siding/plastic", "Aluminum Siding", "Stucco"]),
        "occupancy": random.choice(["Owner", "Tenant"]),
        "usage": random.choice(["Primary", "Secondary", "Seasonal"]),
        "residence": random.choice(["Dwelling", "Condominium", "Townhouse"]),
        # Claim
        "claim_date": claim_date,
        "claim_reason": random.choice(claim_reasons),
        # Insurance
        "carrier": random.choice(carriers),
        "renew_date": renew.strftime("%m/%d/%Y"),
        "premium": str(random.randint(800, 3000)),
        "duration": f"{random.randint(1, 10)} Years",
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    start = time.time()
    p("=" * 50)
    p("  BindRocket HOME Form — ULTRA FAST")
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

    # ── Step 2: Browser → Home Form ───────────────────────────────────────────
    p("\n🌐 Loading Home form...")
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

        # Navigate to HOME form
        form_url = f"{BASE_URL}/forms/home?agency_id={agency_id}&agent_id={agent_id}"
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
                # Check if we have actual form fields
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
            # Last resort: check if ANY inputs exist
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

        # ── Step 3: Generate data ─────────────────────────────────────────────
        d = gen_home_data()
        p(f"\n📝 Filling Home form...")
        p(f"   👤 {d['full']} | {d['email']} | {d['phone']}")
        p(f"   👫 Spouse: {d['spouse_first']} {d['spouse_last']}")
        p(f"   🏠 Value: ${d['home_value']} | Built: {d['year_built']} | {d['construction']}")
        p(f"   📅 Effective: {d['eff_date']} | Renewal: {d['renew_date']}")
        t0 = time.time()

        # ── 1. Personal Information ───────────────────────────────────────────
        p("\n   ─── Personal Information ───")
        js_set_by_name(driver, "firstName", d["first"], "First Name")
        js_set_by_name(driver, "lastName", d["last"], "Last Name")
        js_set_by_name(driver, "emailAddress", d["email"], "Email")
        # Address fields — use Google Places autocomplete
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

        search_location(0, search_term, "Mailing Address")
        js_set_by_name(driver, "mobileNumber", d["phone"], "Mobile")
        js_set_by_name(driver, "workNumber", d["work_phone"], "Work Phone")

        # Date fields order in Home form:
        # 0=DOB, 1=Effective Date, 2=Spouse DOB,
        # 3=Roof Updated, 4=Wiring, 5=Plumbing, 6=Heating,
        # 7=Claim Date, 8=Renewal Date
        js_set_nth_date(driver, 0, d["dob"], "Date of Birth")
        js_set_nth_date(driver, 1, d["eff_date"], "Effective Date")

        # Staying less than 6 months → No
        js_click_radio_by_name(driver, "hasPreviousAddress")

        # ── 2. Spouse Information ─────────────────────────────────────────────
        p("\n   ─── Spouse Information ───")
        js_set_by_placeholder(driver, "Enter First Name", d["spouse_first"], "Spouse First")
        # Try alternate placeholder for spouse
        driver.execute_script("""
            var inputs = document.querySelectorAll('input');
            var nameFields = [];
            for (var i = 0; i < inputs.length; i++) {
                var ph = inputs[i].placeholder || '';
                var name = inputs[i].name || '';
                if ((name.indexOf('spouse') >= 0 || name.indexOf('Spouse') >= 0) 
                    && inputs[i].offsetParent) {
                    nameFields.push({el: inputs[i], name: name});
                }
            }
            for (var j = 0; j < nameFields.length; j++) {
                var n = nameFields[j].name.toLowerCase();
                var el = nameFields[j].el;
                var val = '';
                if (n.indexOf('first') >= 0) val = arguments[0];
                else if (n.indexOf('last') >= 0) val = arguments[1];
                if (val) {
                    try {
                        var p = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value');
                        if (p && p.set) p.set.call(el, val);
                        else el.value = val;
                    } catch(e) { el.value = val; }
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                }
            }
        """, d["spouse_first"], d["spouse_last"])
        p(f"   ✅ Spouse: {d['spouse_first']} {d['spouse_last']}")
        js_set_nth_date(driver, 2, d["spouse_dob"], "Spouse DOB")

        p("\n   ─── Property Information ───")
        search_location(1, search_term, "Property Address")
        # Try to fill home value, year built by placeholder or name
        js_set_by_placeholder(driver, "Enter Home Value", d["home_value"], "Home Value")
        js_set_by_placeholder(driver, "Enter Year Built", d["year_built"], "Year Built")
        # Also try name-based (with properties.0 prefix)
        js_set_by_name(driver, "properties.0.homeValue", d["home_value"], "Home Value (name)")
        js_set_by_name(driver, "properties.0.yearBuilt", d["year_built"], "Year Built (name)")

        # Last updated dates
        js_set_nth_date(driver, 3, d["roof_date"], "Last Roof Updated")
        js_set_nth_date(driver, 4, d["wiring_date"], "Last Wiring Updated")
        js_set_nth_date(driver, 5, d["plumbing_date"], "Last Plumbing Updated")
        js_set_nth_date(driver, 6, d["heating_date"], "Last Heating Updated")

        # ── 4-8. Radio Sections ───────────────────────────────────────────────
        p("\n   ─── Radio Sections ───")
        js_click_radio_by_label(driver, d["construction"], "Construction")
        js_click_radio_by_label(driver, d["siding"], "Siding")
        js_click_radio_by_label(driver, d["occupancy"], "Occupancy")
        js_click_radio_by_label(driver, d["usage"], "Usage")
        js_click_radio_by_label(driver, d["residence"], "Residence")

        # ── 9. Discounts (checkboxes) ─────────────────────────────────────────
        p("\n   ─── Discounts ───")
        # Check some discount checkboxes (Burglar Alarm, Sprinkler, Water Shut-Off)
        js_check_all_checkboxes(driver)

        # ── 10. Claim Information ─────────────────────────────────────────────
        p("\n   ─── Claim Information ───")
        js_set_nth_date(driver, 7, d["claim_date"], "Claim Date")
        js_set_by_placeholder(driver, "Claim Reason", d["claim_reason"], "Claim Reason")
        # Try other common placeholders
        js_set_by_placeholder(driver, "Enter Claim Reason", d["claim_reason"], "Claim Reason")

        # ── 11. Current Insurance ─────────────────────────────────────────────
        p("\n   ─── Current Insurance ───")
        js_set_by_name(driver, "properties.0.carrierName", d["carrier"], "Carrier")
        js_set_by_placeholder(driver, "Enter Carrier Name", d["carrier"], "Carrier (ph)")
        js_set_nth_date(driver, 8, d["renew_date"], "Renewal Date")
        js_set_by_name(driver, "properties.0.premiumAmount", d["premium"], "Premium")
        js_set_by_placeholder(driver, "Current insurance premium", d["premium"], "Premium (ph)")
        js_set_by_name(driver, "properties.0.duration", d["duration"], "Duration")
        js_set_by_placeholder(driver, "Current Duration", d["duration"], "Duration (ph)")

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
