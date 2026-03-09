# BR Leads Management System Automation (US Project)

Ultra-fast automation scripts for the BindRocket Leads Management System. Each script fills and submits a complete insurance application form in under 30 seconds using JavaScript injection for near-instant field population.

## 🚀 Forms Automated

| Script | Form | Fields | Avg Time |
|--------|------|--------|----------|
| `bindrocket_auto.py` | Auto Insurance | 20+ fields | ~23s |
| `bindrocket_home.py` | Home Insurance | 64 fields | ~17s |
| `bindrocket_healthcare.py` | Healthcare | 22 fields | ~27s |

## 📋 Features

- **Ultra-Fast JS Injection** — Fields are set via JavaScript, not `send_keys` (~0.05s per field)
- **Google Places Autocomplete** — Addresses use real Google Places search with US-based selection
- **API Login + TFA Bypass** — Uses API authentication with `authenticated=true` cookie to bypass 2FA
- **Random Realistic Data** — Every run generates fresh US-based data using Faker
- **Lead Source + Save** — Automatically selects a lead source and saves the form
- **Auto-Retry** — Handles slow page loads with retry mechanisms and page refresh

## ⚙️ Setup

### Prerequisites
- Python 3.10+
- Google Chrome browser

### Installation

```bash
# Clone the repo
git clone https://github.com/shrabbi002/BR-Leads-Managament-System-Automation-US-Project.git
cd BR-Leads-Managament-System-Automation-US-Project

# Install dependencies
pip install -r requirements.txt
```

## 🏃 Usage

```bash
# Auto Insurance form
python bindrocket_auto.py

# Home Insurance form
python bindrocket_home.py

# Healthcare form
python bindrocket_healthcare.py
```

Each script will:
1. Login via API (bypasses 2FA)
2. Open Chrome and navigate to the form
3. Fill all fields with random US data
4. Click Save → Select Lead Source → Confirm Save
5. Print a detailed log to console and to a log file

## 📁 Project Structure

```
├── bindrocket_auto.py         # Auto insurance form automation
├── bindrocket_home.py         # Home insurance form automation
├── bindrocket_healthcare.py   # Healthcare form automation
├── tfa_bypass.py              # TFA bypass research script
├── tfa_recon.py               # TFA reconnaissance script
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔑 Environment Configuration

Login credentials and API URLs are configured at the top of each script:

```python
BASE_URL = "https://dev.bindrocket.com"
API_URL = "https://dev-api.bindrocket.com"
EMAIL = "sam201td@gmail.com"
PASSWORD = "Shrabbi1234@#"
```

## 📊 Form Coverage

### Auto Form (`bindrocket_auto.py`)
- Personal Info (name, email, phones, DOB, address)
- Driver Info (name, DOB, license)
- Vehicle Info (coverage type, VIN)
- Current Insurance (carrier, renewal, premium, duration)

### Home Form (`bindrocket_home.py`)
- Personal Info + Spouse Info
- Property Info (value, year built, 4 update dates)
- Construction, Siding, Occupancy, Usage, Residence (radio selections)
- Discounts (checkboxes)
- Claim Info + Current Insurance Carrier

### Healthcare Form (`bindrocket_healthcare.py`)
- Personal Info (name, email, phones, DOB, address)
- Gender + Tobacco Usage (radios)
- Immigration + Employment Status (dropdowns)
- Income Amount
- Dependent Info (name, DOB, gender, immigration, relation, tobacco)

## 🛠️ Technical Details

- **Selenium WebDriver** for browser control
- **JavaScript Injection** for React-controlled input fields
- **Faker** library for realistic US data generation
- **requests** library for API-based login
- **Google Places API** for address autocomplete

---
*Built for rapid form testing and lead generation on the BindRocket platform.*
