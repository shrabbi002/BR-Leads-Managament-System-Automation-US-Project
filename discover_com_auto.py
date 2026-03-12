"""
Discover exact field attributes for the Commercial Auto form.
Navigates to each section and dumps all input placeholders, radio labels, etc.
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

BASE_URL = "https://dev.bindrocket.com"
API_URL = "https://dev-api.bindrocket.com"
EMAIL = "sam201td@gmail.com"
PASSWORD = "Shrabbi1234@#"

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

def main():
    # API Login
    resp = requests.post(f"{API_URL}/api/login", json={"email": EMAIL, "password": PASSWORD})
    data = resp.json()
    ld = data["data"]
    token, user, agent_id = ld["token"], ld["user"], ld["agent_id"]
    agency_id = user["agency_id"]
    print(f"Logged in: {user['firstname']} {user['lastname']}")

    driver = create_driver()
    try:
        driver.get(f"{BASE_URL}/login")
    except TimeoutException:
        pass
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

    # Navigate to form
    form_url = f"{BASE_URL}/forms/commercial_auto?agency_id={agency_id}&agent_id={agent_id}"
    try:
        driver.get(form_url)
    except TimeoutException:
        pass

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter First Name']")))
    except TimeoutException:
        pass
    time.sleep(2)

    # Dismiss overlays
    driver.execute_script("""
        var btns = document.querySelectorAll('button');
        for (var i = 0; i < btns.length; i++) {
            if (btns[i].textContent.trim() === 'Dismiss') { btns[i].click(); break; }
        }
    """)
    time.sleep(0.5)

    sections = [
        "Personal Information",
        "Operations Information", 
        "Driver(s) Information",
        "Vehicle(s) Information",
        "Fillings Information"
    ]

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "com_auto_fields.txt")
    output_file = open(output_path, "w", encoding="utf-8")

    for section_name in sections:
        # Click section
        driver.execute_script("""
            var items = document.querySelectorAll('div, span, li, a, button');
            for (var i = 0; i < items.length; i++) {
                var t = items[i].textContent.trim();
                if (t === arguments[0]) { items[i].click(); break; }
            }
        """, section_name)
        time.sleep(1.5)

        header = f"\n{'='*60}\nSECTION: {section_name}\n{'='*60}\n"
        print(header)
        output_file.write(header)

        # Get all visible inputs
        inputs_info = driver.execute_script("""
            var result = [];
            var inputs = document.querySelectorAll('input, textarea, select');
            for (var i = 0; i < inputs.length; i++) {
                var el = inputs[i];
                if (el.offsetParent === null) continue;
                result.push({
                    tag: el.tagName,
                    type: el.type || '',
                    name: el.name || '',
                    id: el.id || '',
                    placeholder: el.placeholder || '',
                    value: el.value || '',
                    className: (el.className || '').substring(0, 60)
                });
            }
            return result;
        """)

        for inp in inputs_info:
            line = f"  [{inp['tag']}] type={inp['type']} | ph=\"{inp['placeholder']}\" | name=\"{inp['name']}\" | id=\"{inp['id']}\"\n"
            print(line, end="")
            output_file.write(line)

        # Get all radio button groups
        radios_info = driver.execute_script("""
            var result = [];
            var radios = document.querySelectorAll('input[type="radio"]');
            var seen = {};
            for (var i = 0; i < radios.length; i++) {
                var r = radios[i];
                if (r.offsetParent === null) continue;
                var name = r.name || 'unnamed_' + i;
                if (seen[name]) continue;
                seen[name] = true;
                
                // Find the question/label text - look up through parents
                var questionText = '';
                var container = r.parentElement;
                for (var d = 0; d < 8; d++) {
                    if (!container) break;
                    // Look at container's own direct text or child text nodes
                    var children = container.children;
                    for (var c = 0; c < children.length; c++) {
                        var child = children[c];
                        var t = child.textContent.trim();
                        // Look for question text (not Yes/No, not too short)
                        if (t.length > 3 && t !== 'Yes' && t !== 'No' && 
                            t.indexOf('Yes') < 0 && t.indexOf('No') < 0 &&
                            !child.querySelector('input[type="radio"]')) {
                            if (t.length < 120) {
                                questionText = t;
                                break;
                            }
                        }
                    }
                    if (questionText) break;
                    
                    // Also check previous sibling
                    var prev = container.previousElementSibling;
                    if (prev) {
                        var pt = prev.textContent.trim();
                        if (pt.length > 5 && pt.length < 120 && pt.indexOf('Yes') < 0 && pt.indexOf('No') < 0) {
                            questionText = pt;
                            break;
                        }
                    }
                    container = container.parentElement;
                }

                var opts = [];
                var groupRadios = document.querySelectorAll('input[type="radio"][name="' + name + '"]');
                for (var g = 0; g < groupRadios.length; g++) {
                    var optLabel = groupRadios[g].parentElement ? groupRadios[g].parentElement.textContent.trim() : '';
                    opts.push(optLabel);
                }
                
                result.push({
                    name: name,
                    question: questionText,
                    options: opts
                });
            }
            return result;
        """)

        radio_header = "\n  --- RADIO BUTTONS ---\n"
        print(radio_header, end="")
        output_file.write(radio_header)
        for radio in radios_info:
            line = f"  RADIO name=\"{radio['name']}\" | question=\"{radio['question'][:100]}\" | opts={radio['options']}\n"
            print(line, end="")
            output_file.write(line)

    output_file.close()
    print(f"\n\nSaved to {output_path}")
    driver.quit()

if __name__ == "__main__":
    main()
