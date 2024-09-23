# Supreme Court Case Scraper

## Project Overview

This project automates the process of scraping case-related information from the official Supreme Court of Nepal website. It is divided into two tasks:
1. **Today's Case State Scraping**: Extracts the *मुद्दाको प्रक्रियागत विवरण* at specific times daily.
2. **Procedural Case Detail Scraping**: Scrapes detailed information about individual cases using case registration numbers.

Both tasks aim to automate the extraction and storage of data in JSON format.

---

### Task 1: Today's Case State Scraper

**Objective**: Scrape the case details daily at **10:30 AM** and **5:30 PM** from the Supreme Court's website and store the information in a JSON file named `case_state_today.json`.

- **Scraping logic**:
  - Fetches the webpage data.
  - Parses case state data using BeautifulSoup.
  - Saves the parsed information in a structured JSON format.

### Task 2: Procedural Case Detail Scraper

**Objective**: Fetch detailed information for each case using case registration numbers via a POST request and save the result in `procedural_case_detail.json`.

- **Scraping logic**:
  - Sends a POST request with case numbers.
  - Scrapes detailed case information, including registration details, issue specifics, hearing records, and more.
  - Executes scraping tasks concurrently using multithreading for faster performance.

---

### Installation and Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

### Usage Instructions

#### Running Today's Case State Scraper:

1. **Navigate to the project directory**.
2. **Run the scraper**:
   ```bash
   python case_state_scrapper.py
   ```

The program will automatically scrape the data twice a day (at 10:30 AM and 5:30 PM) and save the result in `case_state_today.json`.

#### Running Procedural Case Detail Scraper:

1. Ensure you have a JSON file named `reg_number.json` containing the registration numbers you wish to scrape.
2. **Run the scraper**:
   ```bash
   python case_detail_scrapper.py
   ```

This will initiate scraping for all the registration numbers provided, and the detailed case data will be saved in `procedural_case_detail.json`.

---

### Key Features

- **Automated Scheduling**: Scrapes data at predefined intervals.
- **Concurrent Processing**: Uses multithreading to handle multiple case numbers, significantly improving scraping speed.
- **JSON Storage**: Data is neatly structured and saved in JSON format, ready for API integration or further processing.

---