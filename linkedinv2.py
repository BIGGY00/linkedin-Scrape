import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from urllib.parse import urlencode
from datetime import datetime

# Prevent the ai-block with random delay
def random_delay(min_time=10, max_time=20):
    time.sleep(random.uniform(min_time, max_time))

# Function scrape
def scrape_job_details(keyword):
    # Generate a dynamic database filename with the current date and timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    db_filename = f"job_details_{timestamp}.db"
    
    # Set up SQLite database
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs 
                      (id INTEGER PRIMARY KEY, title TEXT, company TEXT, description TEXT)''')

    # Set up WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # Log in to LinkedIn
        driver.get("https://www.linkedin.com/login")
        random_delay(10, 15)

        # Log in
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password")
        username.send_keys("")  # Replace with your email
        password.send_keys("")  # Replace with your password
        password.send_keys("\n")
        random_delay(10, 15)

        # Navigate to job search
        base_url = "https://www.linkedin.com/jobs/search/"
        params = {"keywords": keyword}
        search_url = f"{base_url}?{urlencode(params)}"
        driver.get(search_url)
        random_delay(15, 20)

        # Extract job details
        job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
        for index, job_card in enumerate(job_cards[:1]):  # Adjust for 800 cards
            job_card.click()
            random_delay(10, 15)

            try:
                job_title = driver.find_element(By.CSS_SELECTOR, "h1.t-24.t-bold.inline a").text
                company_name = driver.find_element(By.CSS_SELECTOR, "div.job-details-jobs-unified-top-card__company-name a").text
                job_description = driver.find_element(By.CSS_SELECTOR, "article.jobs-description__container").text

                # Insert job details into SQLite database
                cursor.execute("INSERT INTO jobs (title, company, description) VALUES (?, ?, ?)",
                               (job_title, company_name, job_description))
                conn.commit()

                print(f"Saved Job {index + 1}: {job_title}")
            except Exception as e:
                print(f"Error processing job {index + 1}: {e}")

    finally:
        # Close resources
        conn.close()
        driver.quit()

# Main function
if __name__ == "__main__":
    # Please enter your keyword
    keyword = "it"
    scrape_job_details(keyword)
