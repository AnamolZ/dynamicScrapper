import schedule
import time
import requests
from lxml import html
from bs4 import BeautifulSoup
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class SupremeCourtCase:
    def __init__(self, reg_no):
        self.reg_no = reg_no
        self.case_details = {}
        self.issue_details = []
        self.date_details = []
        self.nested_table_data = []
        self.hearing_details = []

    def fetch_case_detail_url(self):
        url = "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details"
        data = {
            'syy': '', 'smm': '', 'sdd': '', 'regno': self.reg_no,
            'tyy': '', 'tmm': '', 'tdd': '', 'mode': 'show', 'list': 'list'
        }
        response = requests.post(url, data=data, verify=False)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            anchor_tag = soup.find('a', href=lambda x: x and 'sys.php?d=reports' in x)
            if anchor_tag:
                base_url = "https://supremecourt.gov.np/lic/"
                return base_url + anchor_tag['href'].replace('&amp;', '&')
        return None

    def fetch_case_info(self, case_url):
        response = requests.get(case_url, verify=False)
        response.encoding = 'utf-8'
        tree = html.fromstring(response.content)
        darta_number = (tree.xpath('//td[normalize-space(text())="दर्ता नँ . :"]/following-sibling::td/font/text()') or ["N/A"])[0].strip()
        self.case_details[darta_number] = {
            "मुद्दाको विवरण": {
                "दर्ता नँ": darta_number,
                "दर्ता मिती": self.get_text(tree, '//td[normalize-space(text())="दर्ता मिती:"]/following-sibling::td/font/text()'),
                "रुजु मिती": self.get_text(tree, '//td[normalize-space(text())="रुजु मिती:"]/following-sibling::td/font/text()'),
                "मुद्दाको किसिम": self.get_text(tree, '//td[normalize-space(text())="मुद्दाको किसिम:"]/following-sibling::td/font/text()'),
                "मुद्दा": self.get_text(tree, '//td[normalize-space(text())="मुद्दा:"]/following-sibling::td/font/text()'),
                "फाँटवाला": self.get_text(tree, '//td[normalize-space(text())="फाँटवाला:"]/following-sibling::td/font/text()'),
                "फाँट": self.get_text(tree, '//td[normalize-space(text())="फाँट:"]/following-sibling::td/font/text()'),
                "मुद्दाको स्थिती": self.get_text(tree, '//td[normalize-space(text())="मुद्दाको स्थिती:"]/following-sibling::td/font/text()'),
                "वादीहरु": self.get_text(tree, '//td[normalize-space(text())="वादीहरु :"]/following-sibling::td/font/text()'),
                "प्रतिवादीहरु": self.get_text(tree, '//td[normalize-space(text())="प्रतिवादीहरु :"]/following-sibling::td/font/text()'),
                "वादी अधिवक्ता": self.get_text(tree, '//td[normalize-space(text())="वादी अधिवक्ता(हरु):"]/following-sibling::td/font/text()'),
                "प्रतिवादी अधिवक्ता": self.get_text(tree, '//td[normalize-space(text())="प्रतिवादी अधिवक्ता(हरु):"]/following-sibling::td/font/text()')
            }
        }
        self.parse_issue_details(tree)
        self.parse_date_details(tree)
        self.parse_nested_table_data(tree)
        self.parse_hearing_details(tree)

    def get_text(self, tree, xpath):
        return (tree.xpath(xpath) or ["N/A"])[0].strip()

    def parse_issue_details(self, tree):
        issue_table = tree.xpath('//table')[1]
        rows = issue_table.xpath('.//tr')[1:]
        for row in rows:
            cols = row.xpath('.//td')
            if cols:
                self.issue_details.append({
                    "दर्ता नँ": cols[0].text_content().strip() or "NA",
                    "दर्ता मिती": cols[1].text_content().strip() or "NA",
                    "मुद्दा": cols[2].text_content().strip() or "NA",
                    "वादीहरु": cols[3].text_content().strip() or "NA",
                    "प्रतिवादीहरु": cols[4].text_content().strip() or "NA",
                    "हालको स्थिती": cols[5].text_content().strip() or "NA",
                })
        if not self.issue_details:
            self.issue_details = [self.empty_issue_detail()]

    def empty_issue_detail(self):
        return {
            "दर्ता नँ": "NA",
            "दर्ता मिती": "NA",
            "मुद्दा": "NA",
            "वादीहरु": "NA",
            "प्रतिवादीहरु": "NA",
            "हालको स्थिती": "NA",
        }

    def parse_date_details(self, tree):
        tables = tree.xpath('//table[@class="table-bordered table-striped table-hover"]')
        for table in tables:
            headers = [th.text_content().strip() for th in table.xpath('.//tr[1]/td')]
            data = []
            for row in table.xpath('.//tr[position()>1]'):
                cells = row.xpath('.//td')
                if cells:
                    row_data = {headers[i]: (cells[i].text_content().strip() or "N/A") for i in range(len(cells))}
                    data.append(row_data)
            if headers == ['तारेख मिती', 'विवरण', 'तारेखको किसिम', '']:
                self.date_details = data
                break
        if not self.date_details:
            self.date_details = [self.empty_date_detail()]

    def empty_date_detail(self):
        return {
            "तारेख मिती": "NA",
            "विवरण": "NA",
            "तारेखको किसिम": "NA",
            " ": "NA"
        }

    def parse_nested_table_data(self, tree):
        outer_td_elements = tree.xpath('//td[@colspan="4"]')
        for outer_td in outer_td_elements:
            nested_table = outer_td.xpath('.//table[@class="table-bordered table-striped table-hover"]')
            if nested_table:
                rows = nested_table[0].xpath('.//tr')
                for row in rows[1:]:
                    cols = row.xpath('.//td')
                    if len(cols) == 3:
                        self.nested_table_data.append({
                            "मिती": cols[0].text_content().strip() or "NA",
                            "विवरण": cols[1].text_content().strip() or "NA",
                            "स्थिती": cols[2].text_content().strip() or "NA",
                        })
        if not self.nested_table_data:
            self.nested_table_data = [self.empty_nested_table_data()]

    def empty_nested_table_data(self):
        return {
            "मिती": "NA",
            "विवरण": "NA",
            "स्थिती": "NA"
        }

    def parse_hearing_details(self, tree):
        hearing_table = tree.xpath('//table[@class="table-bordered table-striped table-hover"]')[3]
        headers = [header.text_content().strip() for header in hearing_table.xpath('.//td[position()<5]')]
        for row in hearing_table.xpath('.//tr[position()>1]'):
            cols = row.xpath('.//td')
            if len(cols) == 4:
                entry = {
                    headers[0]: cols[0].text_content().strip() or "N/A",
                    headers[1]: cols[1].text_content().strip() or "N/A",
                    headers[2]: cols[2].text_content().strip() or "N/A",
                    headers[3]: cols[3].text_content().strip() or "N/A"
                }
                self.hearing_details.append(entry)
        if not self.hearing_details:
            self.hearing_details = [self.empty_hearing_detail()]

    def empty_hearing_detail(self):
        return {
            "सुनवाइ मिती": "NA",
            "न्यायाधीशहरू": "NA",
            "मुद्दाको स्थिती": "NA",
            "आदेश /फैसलाको किसिम": "NA"
        }

    def save_data(self):
        merged_data = {
            "लगाब मुद्दाहरुको विवरण": self.issue_details,
            "तारेख विवरण": self.date_details,
            "मुद्दाको स्थितीको बिस्तृत विवरण": self.nested_table_data,
            "पेशी को विवरण": self.hearing_details
        }
        file_path = 'procedural_case_detail.json'
        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
                if not isinstance(existing_data, list):
                    existing_data = []
        existing_data.insert(0, self.case_details)
        existing_data.insert(1, merged_data)
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

def process_case(reg_no):
    case = SupremeCourtCase(reg_no)
    case_detail_url = case.fetch_case_detail_url()
    if case_detail_url:
        case.fetch_case_info(case_detail_url)
        case.save_data()

def main():
    with open('reg_number.json', 'r', encoding='utf-8') as file:
        registration_numbers = json.load(file)
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_case, reg_no): reg_no for reg_no in registration_numbers}
        for future in as_completed(futures):
            reg_no = futures[future]
            try:
                future.result()
                print(f"Data for {reg_no} processed.")
            except Exception as e:
                print(f"Error processing {reg_no}: {e}")

def schedule_task():
    print("Running scheduled task...")
    main()

if __name__ == "__main__":
    schedule.every().day.at("10:30").do(schedule_task)
    schedule.every().day.at("17:30").do(schedule_task)
    while True:
        print("...Waiting Until Scheduled Time...")
        schedule.run_pending()
        time.sleep(60)
