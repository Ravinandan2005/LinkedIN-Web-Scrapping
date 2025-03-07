import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

# ----------------------------
# 6. SETUP LOGGING
# ----------------------------

logging.basicConfig(filename="logs.txt", 
                    level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s", 
                    datefmt="%Y-%m-%d %H:%M:%S")

# ----------------------------
# 1. CONNECT TO DATABASE & CREATE TABLES
# ----------------------------
conn = sqlite3.connect('linkedin.db')
cursor = conn.cursor()

# Table for basic profile info
cursor.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        profile_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_url  TEXT UNIQUE,
        name         TEXT,
        info         TEXT,
        about        TEXT
    )
''')

# Table for skills (one row per skill)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        skill_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id   INTEGER,
        skill_name   TEXT,
        FOREIGN KEY (profile_id) REFERENCES profiles(profile_id) ON DELETE CASCADE
    )
''')

# Table for experience details
cursor.execute('''
    CREATE TABLE IF NOT EXISTS experience (
        exp_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id   INTEGER,
        role         TEXT,
        organization TEXT,
        location     TEXT,
        duration     TEXT,
        FOREIGN KEY (profile_id) REFERENCES profiles(profile_id) ON DELETE CASCADE
    )
''')

# Table for certifications details
cursor.execute('''
    CREATE TABLE IF NOT EXISTS certifications (
        cert_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id   INTEGER,
        cert_name    TEXT,
        provider     TEXT,
        issued       TEXT,
        FOREIGN KEY (profile_id) REFERENCES profiles(profile_id) ON DELETE CASCADE
    )
''')

# Table for education details
cursor.execute('''
    CREATE TABLE IF NOT EXISTS education (
        edu_id           INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id       INTEGER,
        institution_name TEXT,
        FOREIGN KEY (profile_id) REFERENCES profiles(profile_id) ON DELETE CASCADE
    )
''')

conn.commit()

# ----------------------------
# 2. SETUP SELENIUM
# ----------------------------
connections = []
browser = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=browser)
driver.maximize_window()

# Open LinkedIn Login Page
driver.get("https://www.linkedin.com/login")
time.sleep(3)

with open("login.txt", "r") as file:
    details = file.readlines()

driver.find_element(By.ID, "username").send_keys(details[0].strip())
driver.find_element(By.ID, "password").send_keys(details[1].strip())
time.sleep(2)
driver.find_element(By.CLASS_NAME, "btn__primary--large").click()
time.sleep(3)
# print("Logged in!")
logging.info("Logged in!")
time.sleep(5)

# Open connections page
driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
time.sleep(3)

def scroll_down():
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

scroll_down()

def User_url():
    page_source = BeautifulSoup(driver.page_source, 'html.parser')
    profile_links = page_source.find_all('a', class_="ember-view mn-connection-card__picture")
    for link in profile_links:
        profile_url = 'https://linkedin.com' + link.get("href")
        if profile_url not in connections:
            connections.append(profile_url)

User_url()

# (Optional) Click "See more" button if available...
try:
    more_result = driver.find_element(By.CLASS_NAME, "scaffold-finite-scroll__load-button")
    if more_result:
        more_result.click()
        scroll_down()
        time.sleep(2)
        User_url()
except Exception as err:
    pass

# ----------------------------
# 3. SCRAPE & STORE DATA FOR 5 PROFILES
# ----------------------------
# Loop through 5 profiles for testing
for user_url in connections[:5]:
    driver.get(user_url)
    time.sleep(2)
    scroll_down()
    time.sleep(3)
    
    page_source = BeautifulSoup(driver.page_source, 'html.parser')
    
    # --- Basic Profile Info ---
    name_tag = page_source.find('h1')
    name = name_tag.text.strip() if name_tag and name_tag.text.strip() else "NA"
    
    info_div = page_source.find('div', class_="text-body-medium break-words")
    info_text = info_div.get_text().strip() if info_div and info_div.get_text().strip() else "NA"
    
    about_section = page_source.find('div', class_="display-flex ph5 pv3")
    about_text = "NA"
    if about_section:
        about_text = about_section.get_text(separator="\n").strip()
        about_text = about_text.replace("…see more", "").strip() or "NA"
    
    # --- Education (if missing, set as NA) ---
    headers = driver.find_elements(By.TAG_NAME, "h2")
    education_section = None
    for header in headers:
        if "education" in header.text.lower():
            education_section = header.find_element(By.XPATH, "./ancestor::section")
            break
    education_list = []
    if education_section:
        edu_items = education_section.find_elements(By.CSS_SELECTOR, "div.mr1.hoverable-link-text.t-bold")
        for edu_item in edu_items:
            institution = edu_item.text.strip().split("\n")[0]
            if institution:
                education_list.append(institution)
    if not education_list:
        education_list = ["NA"]
    
    # --- Experience ---
    exp_section = None
    for header in headers:
        if "experience" in header.text.lower():
            exp_section = header.find_element(By.XPATH, "./ancestor::section")
            break

    exp_details = []
    if exp_section:
        exp_url = user_url + "details/experience/"
        exp_items = exp_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
        for exp in exp_items:
            try:
                role = exp.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']").text.strip() or "NA"
                try:
                    organization = exp.find_element(By.CSS_SELECTOR, "span.t-14.t-normal:not(.t-black--light)").text.strip() or "NA"
                except:
                    organization = "NA"
                try:
                    duration = exp.find_element(By.CSS_SELECTOR, "span.t-14.t-normal.t-black--light").text.strip() or "NA"
                except:
                    duration = "NA"
                try:
                    location = exp.find_element(By.CSS_SELECTOR, "span.t-14.t-normal.t-black--light + span.t-14.t-normal.t-black--light").text.strip() or "NA"
                except:
                    location = "NA"
    
                exp_details.append({
                    "role": role,
                    "organization": organization,
                    "duration": duration,
                    "location": location
                })
            except Exception as e:
                continue
    # If no experience found, fill with NA row
    if not exp_details:
        exp_details = [{"role": "NA", "organization": "NA", "duration": "NA", "location": "NA"}]
    
    # --- Skills ---
    skills_url = user_url + "details/skills/"
    driver.get(skills_url)
    time.sleep(3)
    scroll_down()
    page_source = BeautifulSoup(driver.page_source, 'html.parser')
    skill_sections = page_source.find_all('li', class_='pvs-list__paged-list-item')
    skills_list = []
    for skill_item in skill_sections:
        skill_span = skill_item.find('span', {'aria-hidden': 'true'})
        if skill_span and skill_span.text.strip():
            skills_list.append(skill_span.text.strip())
    # If no skills found, assign ["NA"]
    if not skills_list:
        skills_list = ["NA"]
    
    # --- Certifications ---
    cert_url = user_url + "details/certifications/"
    driver.get(cert_url)
    time.sleep(3)
    scroll_down()
    page_source = BeautifulSoup(driver.page_source, 'html.parser')
    cert_items = page_source.find_all('li', class_='pvs-list__paged-list-item')
    certifications_list = []
    for c in cert_items:
        try:
            cert_name = c.find('span', {'aria-hidden': 'true'}).text.strip() or "NA"
            try:
                issuer = c.find('span', class_='t-14 t-normal').find('span', {'aria-hidden': 'true'}).text.strip() or "NA"
            except:
                issuer = "NA"
            try:
                issue_date = c.find('span', class_='t-14 t-normal t-black--light').find('span', {'aria-hidden': 'true'}).text.strip() or "NA"
            except:
                issue_date = "NA"
            certifications_list.append({
                "cert_name": cert_name,
                "provider": issuer,
                "issued": issue_date
            })
        except:
            continue
    # If no certifications found, fill with one row of NA
    if not certifications_list:
        certifications_list = [{"cert_name": "NA", "provider": "NA", "issued": "NA"}]
    
    # ----------------------------
    # 4. STORE DATA IN DATABASE (No extra prints, only logs)
    # ----------------------------
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO profiles (profile_url, name, info, about)
            VALUES (?, ?, ?, ?)
        ''', (user_url, name, info_text, about_text))
        conn.commit()
        cursor.execute("SELECT profile_id FROM profiles WHERE profile_url = ?", (user_url,))
        profile_id = cursor.fetchone()[0]
        # print(f"[LOG] Profile stored: {user_url} (ID: {profile_id})")
        logging.info(f"Profile stored: {user_url} (ID: {profile_id})")
    except Exception as e:
        # print(f"[LOG] Error inserting profile for {user_url}: {e}")
        logging.error(f"Error inserting profile for {user_url}: {e}")
        continue

    # Insert education details
    for institution in education_list:
        try:
            cursor.execute('''
                INSERT INTO education (profile_id, institution_name)
                VALUES (?, ?)
            ''', (profile_id, institution))
            conn.commit()
        except Exception as e:
            # print(f"[LOG] Error inserting education for {user_url}: {e}")
            logging.info(f"Error inserting education for {user_url}: {e}")

    # Insert experience details
    for exp in exp_details:
        try:
            cursor.execute('''
                INSERT INTO experience (profile_id, role, organization, location, duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (profile_id, exp["role"], exp["organization"], exp["location"], exp["duration"]))
            conn.commit()
        except Exception as e:
            print(f"[LOG] Error inserting experience for {user_url}: {e}")
    print(f"[LOG] Experience stored for profile: {user_url}")

    try:
        cursor.executemany('''
            INSERT INTO skills (profile_id, skill_name)
            VALUES (?, ?)
        ''', [(profile_id, skill) for skill in skills_list])
        conn.commit()
        logging.info(f"Skills stored for profile {user_url}: {', '.join(skills_list)}")
    except Exception as e:
        logging.error(f"Error inserting skills for {user_url}: {e}")

    # Insert certifications details
    for cert in certifications_list:
        try:
            cursor.execute('''
                INSERT INTO certifications (profile_id, cert_name, provider, issued)
                VALUES (?, ?, ?, ?)
            ''', (profile_id, cert["cert_name"], cert["provider"], cert["issued"]))
            conn.commit()
        except Exception as e:
            # print(f"[LOG] Error inserting certification for {user_url}: {e}")
            logging.error(f"Error inserting certification for {user_url}: {e}")
    # print(f"[LOG] Certifications stored for profile: {user_url}")
    logging.info(f"Certifications stored for profile: {user_url}")

# ----------------------------
# 5. CLEANUP
# ----------------------------
# print("[LOG] Finished processing profiles. Press Enter to close...")
logging.info("Finished processing profiles.")
time.sleep(5)
driver.get("https://www.linkedin.com/m/logout/")
logging.info("Logged out!")
time.sleep(10)
driver.quit()
conn.close()
