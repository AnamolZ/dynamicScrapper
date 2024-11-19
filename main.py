import json
import schedule
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.supreme_court_case import SupremeCourtCase

def process_case(reg_no):
    case = SupremeCourtCase(reg_no)
    case.process_case()

def main():
    try:
        with open('registration_number.json', 'r', encoding='utf-8') as file:
            registration_numbers = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error reading registration numbers: {e}")
        return

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_case, reg_no): reg_no for reg_no in registration_numbers}
        for future in as_completed(futures):
            reg_no = futures[future]
            try:
                future.result()
                print(f"Data for {reg_no} processed.")
            except Exception as e:
                print(f"Error processing {reg_no}: {e}")

def scheduler_job():
    main()

schedule.every().day.at("10:30").do(scheduler_job)
schedule.every().day.at("17:30").do(scheduler_job)

if __name__ == "__main__":
    while True:
        print("...Waiting Until Scheduled Time...")
        schedule.run_pending()
        time.sleep(60)
