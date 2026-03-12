"""
BindRocket Commercial Auto Application Form Automation Script (ULTRA-FAST)
==========================================================================
Fills the Commercial Auto form in ~30 seconds using JavaScript injection.
5 Sections: Personal Information, Operations Information, Driver(s) Information,
            Vehicle(s) Information, Fillings Information

Usage:
    python bindrocket_com_auto.py
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
              logging.FileHandler("com_auto_automation_log.txt", mode="w", encoding="utf-8")])
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


def gen_com_auto_data():
    """Generate all Commercial Auto form data in one shot."""
    fn, ln = fake.first_name(), fake.last_name()
    company = fake.company()
    biz_start = fake.date_between(start_date="-10y", end_date="-1y")
    eff = datetime.now() + timedelta(days=random.randint(1, 30))
    dob = fake.date_of_birth(minimum_age=25, maximum_age=60)

    biz_descriptions = [
        "Trucking", "Delivery Service", "Construction", "Landscaping",
        "Plumbing", "Electrical", "Auto Repair", "Towing",
        "Moving Company", "Courier Service", "Waste Management",
        "Food Delivery", "Freight", "Bus Service", "Taxi",
    ]

    # Realistic VIN
    vin = (str(random.randint(1, 5)) + random.choice("HGFJT") + random.choice("GCBAD")
           + random.choice("CM") + fake.numerify("###") + str(random.randint(0, 9))
           + str(random.randint(0, 9)) + random.choice("ABCDEFGHJKLMNPRSTUVWXYZ")
           + fake.numerify("######"))[:17]

    us_states_abbr = ["TX", "CA", "FL", "NY", "OH", "IL", "GA", "VA", "CO", "AZ",
                      "MI", "NC", "PA", "WA", "OR", "NV", "UT", "MN", "WI", "MO"]

    vehicle_makes = ["Ford", "Chevrolet", "RAM", "GMC", "Freightliner",
                     "Peterbilt", "Kenworth", "International", "Volvo", "Mack"]
    vehicle_models = ["F-150", "Silverado", "Transit", "Sprinter", "ProMaster",
                      "Express", "Savana", "NV200", "E-Series", "Cascadia"]
    body_styles = ["Pickup", "Van", "Box Truck", "Flatbed", "Tractor",
                   "Cargo Van", "Stake Bed", "Dump Truck", "Tanker", "Utility"]

    return {
        # Section 1: Personal Information
        "first": fn, "last": ln, "full": f"{fn} {ln}",
        "email": f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@gmail.com",
        "phone": fake.numerify("(###) ###-####"),
        "mobile": fake.numerify("(###) ###-####"),
        "business_name": company,
        "dba": f"{fn}'s {random.choice(['Transport', 'Trucking', 'Logistics', 'Hauling', 'Fleet Services'])}",
        "eff_date": eff.strftime("%m/%d/%Y"),

        # Section 2: Operations Information
        "biz_desc": random.choice(biz_descriptions),
        "biz_start_date": biz_start.strftime("%m/%d/%Y"),
        "vehicle_usage": random.choice(["Commercial", "Business Use", "Service", "Delivery",
                                         "Long Haul", "Local Delivery", "Construction"]),
        "years_experience": str(random.randint(1, 30)),
        "gross_receipts_last": str(random.randint(100000, 5000000)),
        "gross_receipts_coming": str(random.randint(100000, 5000000)),
        "city_name": random.choice(["Houston", "Los Angeles", "Chicago", "Phoenix",
                                     "Philadelphia", "San Antonio", "Dallas", "Austin"]),
        "cargo_type": random.choice(["General Freight", "Household Goods", "Building Materials",
                                      "Auto Parts", "Electronics", "Food Products", "Machinery"]),
        "num_accidents": str(random.randint(0, 2)),
        "loss_details": fake.sentence(nb_words=8),

        # Section 3: Driver Information
        "dob": dob.strftime("%m/%d/%Y"),
        "license_number": fake.bothify("?#######").upper(),
        "license_type": random.choice(["CDL-A", "CDL-B", "CDL-C", "Class D", "Class E"]),
        "unit_type": random.choice(["Straight Truck", "Tractor Trailer", "Van", "Pickup", "Bus"]),
        "driver_years": str(random.randint(1, 25)),

        # Section 4: Vehicle Information
        "vin": vin,
        "vehicle_year": str(random.randint(2015, 2025)),
        "vehicle_make": random.choice(vehicle_makes),
        "vehicle_model": random.choice(vehicle_models),
        "body_style": random.choice(body_styles),
        "gvw": str(random.choice([5000, 8000, 10000, 14000, 16000, 19500, 26000, 33000])),
        "garaging_address": fake.street_address(),
        "radius": str(random.choice([50, 100, 200, 300, 500])),
        "annual_mileage": str(random.randint(10000, 100000)),
        "rear_axles": str(random.choice([1, 2, 3])),
        "safety_devices": random.choice(["ABS", "Air Bags", "GPS Tracking", "Dash Cam",
                                          "Backup Camera", "Lane Departure Warning"]),

        # Section 5: Fillings Information
        "registration_state": random.choice(us_states_abbr),
        "cargo_states": random.choice(["TX, CA, FL", "NY, PA, OH", "IL, MI, WI", "All States"]),
        "permit_name_address": f"{company}, {fake.address().replace(chr(10), ', ')}",
        "additional_comments": fake.sentence(nb_words=10),
    }


# ── JS Helpers ────────────────────────────────────────────────────────────────

def js_set_by_placeholder(driver, placeholder, value, label=""):
    """Set field by placeholder text (React-compatible with native setter)."""
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input, textarea');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].placeholder === arguments[0] && inputs[i].offsetParent !== null) {
                try {
                    var tag = inputs[i].tagName.toLowerCase();
                    var proto = Object.getOwnPropertyDescriptor(
                        tag === 'textarea' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype, 'value');
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
        p(f"   ✅ {label}: {str(value)[:60]}")
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
    return js_set_nth_placeholder(driver, "MM/DD/YYYY", n, value, label)


def js_set_by_name(driver, name, value, label=""):
    """Set field by name attribute (React-compatible)."""
    result = driver.execute_script("""
        var el = document.querySelector('input[name="' + arguments[0] + '"], textarea[name="' + arguments[0] + '"]');
        if (!el) return 'NOT_FOUND';
        try {
            var tag = el.tagName.toLowerCase();
            var proto = Object.getOwnPropertyDescriptor(
                tag === 'textarea' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype, 'value');
            if (proto && proto.set) proto.set.call(el, arguments[1]);
            else el.value = arguments[1];
        } catch(e) { el.value = arguments[1]; }
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        el.dispatchEvent(new Event('blur', {bubbles: true}));
        return 'OK';
    """, name, str(value))
    if result == "OK":
        p(f"   ✅ {label}: {str(value)[:60]}")
    else:
        p(f"   ⚠️ {label}: not found (name='{name}')")
    return result == "OK"


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


def js_click_radio_by_name(driver, name, value_index=1, label=""):
    """Click a radio button by its name attribute. value_index: 0=Yes/first, 1=No/second."""
    result = driver.execute_script("""
        var radios = document.querySelectorAll('input[type="radio"][name="' + arguments[0] + '"]');
        var visible = [];
        for (var i = 0; i < radios.length; i++) {
            if (radios[i].offsetParent !== null) visible.push(radios[i]);
        }
        if (arguments[1] >= visible.length) return 'NOT_FOUND';
        visible[arguments[1]].click();
        return 'OK';
    """, name, value_index)
    choice = "Yes" if value_index == 0 else ("No" if value_index == 1 else str(value_index))
    if result == "OK":
        p(f"   ✅ Radio [{label}]: {choice}")
    else:
        p(f"   ⚠️ Radio [{label}]: not found (name='{name}')")
    return result == "OK"


def js_click_checkbox_nth(driver, n, label=""):
    """Click the nth visible checkbox (0-indexed)."""
    result = driver.execute_script("""
        var cbs = document.querySelectorAll('input[type="checkbox"]');
        var visible = [];
        for (var i = 0; i < cbs.length; i++) {
            if (cbs[i].offsetParent !== null) visible.push(cbs[i]);
        }
        if (arguments[0] >= visible.length) return 'NOT_FOUND';
        if (!visible[arguments[0]].checked) {
            visible[arguments[0]].click();
            return 'OK';
        }
        return 'ALREADY';
    """, n)
    if result == "OK":
        p(f"   ✅ Checkbox [{label}]: checked")
    elif result == "ALREADY":
        p(f"   ℹ️ Checkbox [{label}]: already checked")
    else:
        p(f"   ⚠️ Checkbox [{label}]: not found")
    return result in ("OK", "ALREADY")


def js_select_first_option(driver, label=""):
    """Select the first non-empty option in a visible <select> element."""
    result = driver.execute_script("""
        var selects = document.querySelectorAll('select');
        for (var i = 0; i < selects.length; i++) {
            if (selects[i].offsetParent !== null) {
                for (var o = 1; o < selects[i].options.length; o++) {
                    if (selects[i].options[o].value) {
                        selects[i].selectedIndex = o;
                        selects[i].dispatchEvent(new Event('change', {bubbles: true}));
                        return selects[i].options[o].text;
                    }
                }
            }
        }
        return null;
    """)
    if result:
        p(f"   ✅ {label}: {result}")
    else:
        p(f"   ⚠️ {label}: no select found or no options")
    return result is not None


def click_sidebar(driver, section_name):
    """Click a sidebar/anchor section by name."""
    driver.execute_script("""
        var items = document.querySelectorAll('div, span, li, a, button');
        for (var i = 0; i < items.length; i++) {
            var t = items[i].textContent.trim();
            if (t === arguments[0]) { items[i].click(); break; }
        }
    """, section_name)
    time.sleep(0.8)


def main():
    start = time.time()
    p("=" * 65)
    p("  BindRocket Commercial Auto Application — ULTRA FAST")
    p(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p("=" * 65)

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

    # ── Step 2: Browser → Commercial Auto Form ───────────────────────────────
    p("\n🌐 Opening browser + loading Commercial Auto form...")
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

        for key in ["billing", "package_info"]:
            driver.execute_script(f"localStorage.setItem('{key}', '{json.dumps(ld.get(key, {}))}');")
        driver.execute_script(f"localStorage.setItem('billing_addons', '{json.dumps(ld.get('billingAddons', []))}');")

        # Navigate to Commercial Auto form
        form_url = f"{BASE_URL}/forms/commercial_auto?agency_id={agency_id}&agent_id={agent_id}"
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
                if (btns[i].textContent.trim() === 'Dismiss') { btns[i].click(); break; }
            }
        """)
        time.sleep(0.5)

        p(f"   ✅ Commercial Auto Form ready ({time.time()-t0:.1f}s)")

        # ── Step 3: Generate fresh data ───────────────────────────────────────
        d = gen_com_auto_data()
        p(f"\n📝 Filling Commercial Auto Form...")
        p(f"   👤 {d['full']} | {d['email']} | {d['phone']}")
        p(f"   🏢 {d['business_name']} | DBA: {d['dba']}")
        p(f"   📅 Effective: {d['eff_date']} | Biz Start: {d['biz_start_date']}")
        p(f"   🚛 VIN: {d['vin']} | {d['vehicle_year']} {d['vehicle_make']} {d['vehicle_model']}")
        p(f"   🪪 License: {d['license_number']} | Type: {d['license_type']}")
        t0 = time.time()

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 1: Personal Information
        # ══════════════════════════════════════════════════════════════════════
        p("\n── Section 1: Personal Information ──")

        js_set_by_placeholder(driver, "Enter First Name", d["first"], "First Name")
        js_set_by_placeholder(driver, "Enter Last Name", d["last"], "Last Name")
        js_set_by_placeholder(driver, "Enter Email Address", d["email"], "Email Address")
        js_set_by_name(driver, "businessName", d["business_name"], "Business Name")
        js_set_by_name(driver, "dbaname", d["dba"], "DBA")

        # Phone numbers (name-based)
        js_set_by_name(driver, "workNum", d["phone"], "Work Phone")
        js_set_by_name(driver, "mobileNumber", d["mobile"], "Mobile Number")

        # Effective Date (1st MM/DD/YYYY)
        js_set_nth_date(driver, 0, d["eff_date"], "Effective Date")

        # Entity Type radio (name=entityType, 0=Individual, 1=Partnership, 2=Corporation, 3=Other)
        entity_map = {"Individual": 0, "Partnership": 1, "Corporation": 2, "Other": 3}
        entity_choice = random.choice(list(entity_map.keys()))
        js_click_radio_by_name(driver, "entityType", entity_map[entity_choice], f"Entity Type: {entity_choice}")

        # Location Address (Google Places)
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
        time.sleep(0.5)

        # "Same as Location" checkbox (1st visible checkbox)
        js_click_checkbox_nth(driver, 0, "Same as Location Address")
        time.sleep(0.3)

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 2: Operations Information
        # ══════════════════════════════════════════════════════════════════════
        p("\n── Section 2: Operations Information ──")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.3)
        click_sidebar(driver, "Operations Information")

        # Business Description (searchable) — name=businessDesc_label
        js_select_business_desc(driver, d["biz_desc"])

        # Business Start Date (2nd MM/DD/YYYY on page)
        js_set_nth_date(driver, 1, d["biz_start_date"], "Business Start Date")

        # Vehicle Usage — name=vehicleUsage
        js_set_by_name(driver, "vehicleUsage", d["vehicle_usage"], "Vehicle Usage")

        # New Venture — name=newVenture (0=Yes, 1=No)
        js_click_radio_by_name(driver, "newVenture", 1, "New Venture")

        # Years of Experience — name=yearsOfExperience
        js_set_by_name(driver, "yearsOfExperience", d["years_experience"], "Years of Experience")

        # Is this your primary business? — name=isPrimary
        js_click_radio_by_name(driver, "isPrimary", 0, "Primary Business")

        # Do you haul for hire? — name=isHaul
        js_click_radio_by_name(driver, "isHaul", 1, "Haul for Hire")

        # Do you haul your own cargo exclusively? — name=haulByOwn
        js_click_radio_by_name(driver, "haulByOwn", 0, "Own Cargo Exclusive")

        # Gross Receipts Last Year — name=grossReceipts
        js_set_by_name(driver, "grossReceipts", d["gross_receipts_last"], "Gross Receipts Last Year")

        # Estimate Gross Receipts For Coming Year — name=grossRecieptsUpcoming
        js_set_by_name(driver, "grossRecieptsUpcoming", d["gross_receipts_coming"], "Gross Receipts Coming Year")

        # Do you operate in more than one state? — name=operateArea
        js_click_radio_by_name(driver, "operateArea", 1, "Operate Multi-State")

        # Name of the City — name=cityName
        js_set_by_name(driver, "cityName", d["city_name"], "Largest City")

        # Do you do repossessions? — name=isRepossessions
        js_click_radio_by_name(driver, "isRepossessions", 1, "Repossessions")

        # Do you operate over a regular route? — name=isOperated
        js_click_radio_by_name(driver, "isOperated", 1, "Regular Route")

        # Are you a common carrier? — name=isCommonCarrier
        js_click_radio_by_name(driver, "isCommonCarrier", 1, "Common Carrier")

        # Are you a contract hauler? — name=isContractHauler
        js_click_radio_by_name(driver, "isContractHauler", 1, "Contract Hauler")

        # Types of Cargo Hauled — name=cargoType
        js_set_by_name(driver, "cargoType", d["cargo_type"], "Cargo Type")

        # Do you Haul Hazardous Materials? — name=haulMaterials
        js_click_radio_by_name(driver, "haulMaterials", 1, "Haul Hazardous Materials")

        # Do You Pull Double Trailers? — name=pullDouble
        js_click_radio_by_name(driver, "pullDouble", 1, "Pull Double Trailers")

        # Do You Pull Triple Trailers? — name=pullTriple
        js_click_radio_by_name(driver, "pullTriple", 1, "Pull Triple Trailers")

        # Do You Rent or Lease Your Vehicle to Others? — name=isRenting
        js_click_radio_by_name(driver, "isRenting", 1, "Rent/Lease Vehicle")

        # Do you hire any vehicles? — name=hasVehicle
        js_click_radio_by_name(driver, "hasVehicle", 1, "Hire Vehicles")

        # Loss Experience
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.4);")
        time.sleep(0.3)

        # Have you ever been declined? — name=wasDeclined
        js_click_radio_by_name(driver, "wasDeclined", 1, "Declined/Canceled")

        # Have you previously had commercial auto insurance? — name=hasCommercialAuto
        js_click_radio_by_name(driver, "hasCommercialAuto", 0, "Previous Comm. Auto Insurance")

        # Number of Accidents — name=noOfAccidents
        js_set_by_name(driver, "noOfAccidents", d["num_accidents"], "Number of Accidents")

        # Provide Details of Losses — name=lossDetail
        js_set_by_name(driver, "lossDetail", d["loss_details"], "Loss Details")

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 3: Driver(s) Information
        # ══════════════════════════════════════════════════════════════════════
        p("\n── Section 3: Driver(s) Information ──")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.3)
        click_sidebar(driver, "Driver(s) Information")

        # Same as Applicant checkbox (2nd visible checkbox on page)
        js_click_checkbox_nth(driver, 1, "Same as Applicant")
        time.sleep(0.3)

        # Driver Name
        js_set_by_placeholder(driver, "Enter Driver Name", d["full"], "Driver Name")

        # Driver DOB (3rd MM/DD/YYYY on page — after Effective Date & Biz Start Date)
        js_set_nth_date(driver, 2, d["dob"], "Driver DOB")

        # License State (select dropdown)
        js_select_first_option(driver, "License State")

        # License Number
        js_set_by_placeholder(driver, "Enter License No.", d["license_number"], "License Number")

        # License Type
        js_set_by_placeholder(driver, "Enter Type", d["license_type"], "License Type")

        # Unit Type
        js_set_by_placeholder(driver, "Enter Unit Type", d["unit_type"], "Unit Type")

        # Years (driving experience)
        js_set_by_placeholder(driver, "Enter Years", d["driver_years"], "Driver Years")

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 4: Vehicle(s) Information
        # ══════════════════════════════════════════════════════════════════════
        p("\n── Section 4: Vehicle(s) Information ──")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.3)
        click_sidebar(driver, "Vehicle(s) Information")

        # VIN — ph="Enter 17-character VIN"
        js_set_by_placeholder(driver, "Enter 17-character VIN", d["vin"], "VIN")

        # Year — ph="e.g. 2020"
        js_set_by_placeholder(driver, "e.g. 2020", d["vehicle_year"], "Vehicle Year")

        # Make — ph="e.g. Volvo"
        js_set_by_placeholder(driver, "e.g. Volvo", d["vehicle_make"], "Vehicle Make")

        # Model — ph="e.g. FH16"
        js_set_by_placeholder(driver, "e.g. FH16", d["vehicle_model"], "Vehicle Model")

        # Body Style — ph="Pickup, Wrecker, etc."
        js_set_by_placeholder(driver, "Pickup, Wrecker, etc.", d["body_style"], "Body Style")

        # GVW — ph="Enter GVW"
        js_set_by_placeholder(driver, "Enter GVW", d["gvw"], "GVW")

        # Garaging Address — ph="Enter Garaging Address" (this is a location-search-input)
        search_location(2, search_term, "Garaging Address")

        # Radius — ph="Unl." (1st)
        js_set_nth_placeholder(driver, "Unl.", 0, d["radius"], "Radius")

        # Annual Mileage — ph="Unl." (2nd)
        js_set_nth_placeholder(driver, "Unl.", 1, d["annual_mileage"], "Annual Mileage")

        # Rear Axles — ph="Enter Number"
        js_set_by_placeholder(driver, "Enter Number", d["rear_axles"], "Rear Axles")

        # Safety Devices — ph="Enter Safety Devices"
        js_set_by_placeholder(driver, "Enter Safety Devices", d["safety_devices"], "Safety Devices")

        # ══════════════════════════════════════════════════════════════════════
        # SECTION 5: Fillings Information
        # ══════════════════════════════════════════════════════════════════════
        p("\n── Section 5: Fillings Information ──")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.3)
        click_sidebar(driver, "Fillings Information")

        # Is an FHWA filing required? — name=isFhwaRequired
        js_click_radio_by_name(driver, "isFhwaRequired", 1, "FHWA Filing Required")

        # Authority Type — name=authorityType (0=Broker, 1=Common, 2=Contract)
        authority_idx = random.randint(0, 2)
        authority_labels = ["Broker", "Common", "Contract"]
        js_click_radio_by_name(driver, "authorityType", authority_idx, f"Authority Type: {authority_labels[authority_idx]}")

        # Registration/Base State — name=isInterstateCarrier
        js_set_by_name(driver, "isInterstateCarrier", d["registration_state"], "Registration State")

        # Is an intrastate filing needed? — name=isIntrastate
        js_click_radio_by_name(driver, "isIntrastate", 1, "Intrastate Filing")

        # Cargo Filings States — name=listOfStates
        js_set_by_name(driver, "listOfStates", d["cargo_states"], "Cargo Filing States")

        # Permit Name & Address — name=permitsIssued
        js_set_by_name(driver, "permitsIssued", d["permit_name_address"], "Permit Name & Address")

        # Is MCS 90 endorsement needed? — name=isMCS
        js_click_radio_by_name(driver, "isMCS", 1, "MCS 90 Endorsement")

        # Policy covers all vehicles? — name=isPolicyCovered
        js_click_radio_by_name(driver, "isPolicyCovered", 0, "Policy Covers All Vehicles")

        # Are oversize/overweight commodities hauled? — name=isOversize
        js_click_radio_by_name(driver, "isOversize", 1, "Oversize/Overweight")

        # Are escort vehicles towed on return trips? — name=isTowed
        js_click_radio_by_name(driver, "isTowed", 1, "Escort Vehicles Towed")

        # Transportation of hazardous commodities? — name=isAllowed
        js_click_radio_by_name(driver, "isAllowed", 1, "Authority Hazardous Transport")

        # Allow others to haul hazardous? — name=isOthersAllowed
        js_click_radio_by_name(driver, "isOthersAllowed", 1, "Others Haul Hazardous")

        # Do you enter Canada? — name=isCanada
        js_click_radio_by_name(driver, "isCanada", 1, "Enter Canada")

        # Do you enter Mexico? — name=isMexico
        js_click_radio_by_name(driver, "isMexico", 1, "Enter Mexico")

        # Have you ever changed your operating name? — name=isNameChanged
        js_click_radio_by_name(driver, "isNameChanged", 1, "Name Changed")

        # Do you operate under any other name? — name=isOtherCompany
        js_click_radio_by_name(driver, "isOtherCompany", 1, "Other Company Name")

        # Do you operate as a subsidiary? — name=isSubsidiary
        js_click_radio_by_name(driver, "isSubsidiary", 1, "Subsidiary")

        # Other transportation operations not covered? — name=isTransportationManaged
        js_click_radio_by_name(driver, "isTransportationManaged", 1, "Other Transport Ops")

        # Do you lease your authority? — name=isLeased
        js_click_radio_by_name(driver, "isLeased", 1, "Lease Authority")

        # Do you appoint agents/contractors? — name=hasAgentApointment
        js_click_radio_by_name(driver, "hasAgentApointment", 1, "Appoint Agents")

        # Agreements with other carriers? — name=hasAgreements
        js_click_radio_by_name(driver, "hasAgreements", 1, "Carrier Agreements")

        # Additional Comments — name=additionalComments
        js_set_by_name(driver, "additionalComments", d["additional_comments"], "Additional Comments")

        p(f"\n   ⚡ Commercial Auto Form filled in {time.time()-t0:.1f}s")

        # ── Step 4: Save ──────────────────────────────────────────────────────
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
            p("📋 Lead Source modal detected...")
            lead_sources = ["Call", "SMS", "Friend", "Web", "Third party", "Renewal"]
            chosen = random.choice(lead_sources)

            driver.execute_script("""
                var els = document.querySelectorAll('div, span');
                for (var i = 0; i < els.length; i++) {
                    var t = els[i].textContent.trim();
                    if (t === 'Lead source' || t === 'Lead Source') { els[i].click(); break; }
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
                    if (btns[i].textContent.trim() === 'Save') { btns[i].click(); return; }
                }
            """)
            p("   ✅ Lead Source saved!")
            time.sleep(1)
        else:
            p("   ℹ️ No Lead Source modal detected")

        elapsed = time.time() - start
        p(f"\n{'=' * 65}")
        p(f"  ✅ Commercial Auto Form Done in {elapsed:.1f}s")
        p(f"  📍 URL: {driver.current_url}")
        p("=" * 65)

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
