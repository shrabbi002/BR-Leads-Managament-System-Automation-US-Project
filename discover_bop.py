"""Quick script to discover BOP form fields using API auth + cookie injection."""
import sys, os, time, json, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

BASE_URL = "https://dev.bindrocket.com"
API_URL = "https://dev-api.bindrocket.com"
EMAIL = "sam201td@gmail.com"
PASSWORD = "Shrabbi1234@#"
OUTPUT = "bop_fields.txt"

out = open(OUTPUT, "w", encoding="utf-8")
def p(msg):
    print(msg); out.write(msg + "\n"); out.flush()

# API Login
resp = requests.post(f"{API_URL}/api/login", json={"email": EMAIL, "password": PASSWORD})
data = resp.json()
ld = data["data"]
token, user, agent_id = ld["token"], ld["user"], ld["agent_id"]
agency_id = user["agency_id"]
p(f"Logged in. agency_id={agency_id}, agent_id={agent_id}")

# Browser
opts = Options()
opts.add_argument("--start-maximized")
opts.add_argument("--log-level=3")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
svc = Service(log_output=os.devnull)
driver = webdriver.Chrome(options=opts, service=svc)
driver.set_page_load_timeout(30)

# Set cookies
try:
    driver.get(f"{BASE_URL}/login")
except: pass
time.sleep(1)

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

for key in ["billing", "package_info"]:
    driver.execute_script(f"localStorage.setItem('{key}', '{json.dumps(ld.get(key, {}))}');")
driver.execute_script(f"localStorage.setItem('billing_addons', '{json.dumps(ld.get('billingAddons', []))}');")

# Try BOP URLs
urls_to_try = [
    "/forms/bop",
    "/forms/business_owners_policy",
    "/forms/business_owner_policy",
    "/forms/businessowners",
]

working_url = None
for url_path in urls_to_try:
    form_url = f"{BASE_URL}{url_path}?agency_id={agency_id}&agent_id={agent_id}"
    p(f"\nTrying: {form_url}")
    try:
        driver.get(form_url)
    except TimeoutException:
        p("  Timeout, continuing...")
    time.sleep(3)
    
    current = driver.current_url
    p(f"  Current URL: {current}")
    
    if "login" in current.lower() and url_path not in current:
        p("  Redirected to login - skipping")
        continue
    
    h1 = driver.execute_script("""
        var h = document.querySelector('h1, h2, h3');
        return h ? h.textContent.trim() : '';
    """)
    p(f"  Heading: {h1}")
    
    if h1 and "login" not in h1.lower():
        working_url = url_path
        p(f"\n*** FOUND WORKING URL: {url_path} ***")
        break

if not working_url:
    p("\nNo working URL found!")
    driver.quit()
    out.close()
    sys.exit(1)

# Dismiss any error
driver.execute_script("""
    var btns = document.querySelectorAll('button');
    for (var i = 0; i < btns.length; i++) {
        if (btns[i].textContent.trim() === 'Dismiss') btns[i].click();
    }
""")
time.sleep(0.5)

# Get sidebar sections
sidebar = driver.execute_script("""
    var results = [];
    var els = document.querySelectorAll('[class*="sidebar"] div, [class*="side"] div, [class*="nav"] div, [class*="step"] div');
    for (var i = 0; i < els.length; i++) {
        var t = els[i].textContent.trim();
        if (t.length > 3 && t.length < 60 && els[i].offsetParent !== null) {
            var rect = els[i].getBoundingClientRect();
            if (rect.x < 300) results.push(t);
        }
    }
    return [...new Set(results)].slice(0, 20);
""")
p(f"\nSidebar items: {sidebar}")

# Function to dump all visible inputs
def dump_inputs(section_name):
    p(f"\n=== {section_name} ===")
    inputs = driver.execute_script("""
        var results = [];
        var els = document.querySelectorAll('input, textarea, select');
        for (var i = 0; i < els.length; i++) {
            if (els[i].offsetParent !== null) {
                results.push({
                    tag: els[i].tagName.toLowerCase(),
                    type: els[i].type || '',
                    name: els[i].name || '',
                    placeholder: els[i].placeholder || '',
                    id: els[i].id || ''
                });
            }
        }
        return results;
    """)
    p(f"Found {len(inputs)} visible inputs:")
    for inp in inputs:
        p(f"  <{inp['tag']}> type={inp['type']} name='{inp['name']}' ph='{inp['placeholder']}' id='{inp['id']}'")
    
    # Also find labels
    labels = driver.execute_script("""
        var results = [];
        var els = document.querySelectorAll('label, h4, h5, h6');
        for (var i = 0; i < els.length; i++) {
            var t = els[i].textContent.trim();
            if (t.length > 1 && t.length < 80 && els[i].offsetParent !== null) {
                results.push(t);
            }
        }
        return [...new Set(results)];
    """)
    p(f"\nLabels: {labels}")
    
    # Find radio button groups
    radios = driver.execute_script("""
        var results = [];
        var els = document.querySelectorAll('input[type="radio"]');
        for (var i = 0; i < els.length; i++) {
            if (els[i].offsetParent !== null) {
                var label = els[i].parentElement ? els[i].parentElement.textContent.trim() : '';
                results.push({name: els[i].name, value: els[i].value, label: label});
            }
        }
        return results;
    """)
    if radios:
        p(f"\nRadio buttons:")
        for r in radios:
            p(f"  name='{r['name']}' value='{r['value']}' label='{r['label']}'")
    
    # Find checkboxes
    cbs = driver.execute_script("""
        var results = [];
        var els = document.querySelectorAll('input[type="checkbox"]');
        for (var i = 0; i < els.length; i++) {
            if (els[i].offsetParent !== null) {
                var label = els[i].parentElement ? els[i].parentElement.textContent.trim() : '';
                results.push({name: els[i].name, label: label});
            }
        }
        return results;
    """)
    if cbs:
        p(f"\nCheckboxes:")
        for c in cbs:
            p(f"  name='{c['name']}' label='{c['label']}'")

# Dump Section 1 (default)
dump_inputs("Section 1 (default view)")

# Try clicking section 2
sections_to_click = [
    "BOP Information", "BOP Details", "Property Information",
    "General Liability & Limit", "Coverage Information",
    "Property", "Liability"
]
for sec_name in sections_to_click:
    clicked = driver.execute_script(f"""
        var items = document.querySelectorAll('div, span, li, a, button');
        for (var i = 0; i < items.length; i++) {{
            var t = items[i].textContent.trim();
            if (t === '{sec_name}') {{ items[i].click(); return t; }}
        }}
        return null;
    """)
    if clicked:
        p(f"\nClicked sidebar: '{clicked}'")
        time.sleep(1)
        dump_inputs(f"After clicking '{clicked}'")

# Also try scrolling and looking for more sections
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(0.5)

# Get ALL text on the page that could be section headers
headers = driver.execute_script("""
    var results = [];
    var els = document.querySelectorAll('h1, h2, h3, h4, h5, h6, [class*="header"], [class*="title"], [class*="section"]');
    for (var i = 0; i < els.length; i++) {
        var t = els[i].textContent.trim();
        if (t.length > 2 && t.length < 100 && els[i].offsetParent !== null) {
            results.push(t);
        }
    }
    return [...new Set(results)];
""")
p(f"\nAll headers on page: {headers}")

p("\nDone!")
out.close()
driver.quit()
