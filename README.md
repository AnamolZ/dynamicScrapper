# Court Case Scraper

## Project Overview

The **Court Case Scraper** is an automated tool designed to extract case-related information from the official website of the Supreme Court of Nepal. The project is composed of two main tasks: the first involves extracting procedural case data at scheduled intervals, and the second focuses on scraping detailed case information using registration numbers. These tasks automate the data extraction process, storing the results in a structured JSON format for easy access and further analysis.

The scraper is configured to run at fixed times daily, specifically at **10:30 AM** and **5:30 PM**, to extract procedural case data. This data is saved in a JSON file named `case_state_today.json`. In addition to procedural case data, the scraper also fetches detailed information by sending POST requests with case registration numbers. The detailed case data is stored in a separate JSON file, `procedural_case_detail.json`.

## Key Features

The scraper operates on an automated schedule, ensuring that data is collected consistently twice a day at the designated times. Multithreading is used to efficiently process multiple cases simultaneously, significantly speeding up the scraping process. All the data extracted is saved in a clean, structured JSON format, making it easy to integrate into other systems or perform additional analysis.

## Running the Scraper

To run the scraper, first prepare a JSON file named `reg_number.json`, which should contain the registration numbers of the cases you wish to scrape. Once the file is ready, execute the following command to initiate the scraper:

```bash
python case_detail_scraper.py
```

The scraper will fetch the relevant case details and store them in the `procedural_case_detail.json` file for further use.
