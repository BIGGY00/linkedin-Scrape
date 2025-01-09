import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from urllib.parse import urlencode
from datetime import datetime

# Prevent the AI-block with random delay
def random_delay(min_time=10, max_time=20):
    time.sleep(random.uniform(min_time, max_time))

# Scroll the page to the bottom
def scroll_down(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    random_delay(2, 4)

# Function to scrape job details
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
        username.send_keys("your_email@example.com")  # Replace with your email
        password.send_keys("your_password")  # Replace with your password
        password.send_keys("\n")
        random_delay(10, 15)

        # Navigate to job search
        base_url = "https://www.linkedin.com/jobs/search/"
        params = {"keywords": keyword}
        search_url = f"{base_url}?{urlencode(params)}"
        driver.get(search_url)
        random_delay(15, 20)

        # Extract job details
        scraped_jobs = 0
        max_jobs = 800  # Adjust the number of jobs you want to scrape
        while scraped_jobs < max_jobs:
            job_cards = driver.find_elements(By.CLASS_NAME, "job-card-container")
            for index, job_card in enumerate(job_cards[scraped_jobs:], start=scraped_jobs + 1):
                if scraped_jobs >= max_jobs:
                    break
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

                    print(f"Saved Job {index}: {job_title}")
                    scraped_jobs += 1
                except Exception as e:
                    print(f"Error processing job {index}: {e}")

            # Scroll to load more job cards
            scroll_down(driver)
            random_delay(5, 10)
    
    finally:
        # Close resources
        conn.close()
        driver.quit()

# Main function
if __name__ == "__main__":
    # Please enter your keyword
    keyword = "it"
    scrape_job_details(keyword)
