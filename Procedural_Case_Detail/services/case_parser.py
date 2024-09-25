import requests
from lxml import html
import yaml

class CaseParser:
    def __init__(self):
        with open('config.yml', 'r', encoding='utf-8') as file:
            self.case_service = yaml.safe_load(file)
        with open('case_service.yml', 'r', encoding='utf-8') as xpath_file:
            self.xpath = yaml.safe_load(xpath_file)
        
        self.case_details = {}
        self.issue_details = []
        self.date_details = []
        self.nested_table_data = []
        self.hearing_details = []

    def parse_case_info(self, case_url):
        response = requests.get(case_url, verify=False)
        response.encoding = 'utf-8'
        tree = html.fromstring(response.content)
        registration_number = self.get_text(tree, self.xpath.get('registration_number', 'N/A'))

        self.case_details[registration_number] = {
            self.case_service['case_description']: {
                self.case_service['registration_number']: self.get_text(tree, self.xpath.get('registration_number', 'N/A')),
                self.case_service['registration_date']: self.get_text(tree, self.xpath.get('registration_date', 'N/A')),
                self.case_service['event_date']: self.get_text(tree, self.xpath.get('event_date', 'N/A')),
                self.case_service['case_type']: self.get_text(tree, self.xpath.get('case_type', 'N/A')),
                self.case_service['case']: self.get_text(tree, self.xpath.get('case', 'N/A')),
                self.case_service['clause_holder']: self.get_text(tree, self.xpath.get('clause_holder', 'N/A')),
                self.case_service['clause']: self.get_text(tree, self.xpath.get('clause', 'N/A')),
                self.case_service['case_status']: self.get_text(tree, self.xpath.get('case_status', 'N/A')),
                self.case_service['plaintiffs']: self.get_text(tree, self.xpath.get('plaintiffs', 'N/A')),
                self.case_service['defendants']: self.get_text(tree, self.xpath.get('defendants', 'N/A')),
                self.case_service['plaintiff_attorneys']: self.get_text(tree, self.xpath.get('plaintiff_attorneys', 'N/A')),
                self.case_service['defendant_attorneys']: self.get_text(tree, self.xpath.get('defendant_attorneys', 'N/A'))
            }
        }

        self.get_attachment_details(tree)
        self.get_date_details(tree)
        self.get_case_status_details(tree)
        self.get_hearing_details(tree)

    def get_text(self, tree, xpath):
        if xpath == 'N/A':
            return "N/A"
        result = tree.xpath(xpath)
        if not result:
            return "N/A"
        return result[0].strip()

    def get_attachment_details(self, tree):
        issue_table = tree.xpath('//table')[1]
        rows = issue_table.xpath('.//tr')[1:]
        for row in rows:
            cols = row.xpath('.//td')
            if cols:
                self.issue_details.append({
                    self.case_service['registration_number']: cols[0].text_content().strip() or "NA",
                    self.case_service['registration_date']: cols[1].text_content().strip() or "NA",
                    self.case_service['case']: cols[2].text_content().strip() or "NA",
                    self.case_service['plaintiffs']: cols[3].text_content().strip() or "NA",
                    self.case_service['defendants']: cols[4].text_content().strip() or "NA",
                    self.case_service['current_status']: cols[5].text_content().strip() or "NA",
                })
        if not self.issue_details:
            self.issue_details = [self.empty_attachment_details()]

    def empty_attachment_details(self):
        return {
            self.case_service['registration_number']: "NA",
            self.case_service['registration_date']: "NA",
            self.case_service['case']: "NA",
            self.case_service['plaintiffs']: "NA",
            self.case_service['defendants']: "NA",
            self.case_service['current_status']: "NA",
        }

    def get_date_details(self, tree):
        tables = tree.xpath('//table[@class="table-bordered table-striped table-hover"]')
        for table in tables:
            headers = [th.text_content().strip() for th in table.xpath('.//tr[1]/td')]
            data = []
            for row in table.xpath('.//tr[position()>1]'):
                cells = row.xpath('.//td')
                if cells:
                    row_data = {headers[i]: (cells[i].text_content().strip() or "N/A") for i in range(len(cells))}
                    data.append(row_data)

            date_hearing = self.case_service['date_hearing']
            description = self.case_service['description']
            date_types = self.case_service['date_types']

            if headers == [date_hearing, description, date_types, '']:
                self.date_details = data
                break
        if not self.date_details:
            self.date_details = [self.empty_date_detail()]

    def empty_date_detail(self):
        return {
            self.case_service['date_hearing']: "NA",
            self.case_service['description']: "NA",
            self.case_service['date_types']: "NA",
            " ": "NA"
        }

    def get_case_status_details(self, tree):
        outer_td_elements = tree.xpath('//td[@colspan="4"]')
        for outer_td in outer_td_elements:
            nested_table = outer_td.xpath('.//table[@class="table-bordered table-striped table-hover"]')
            if nested_table:
                rows = nested_table[0].xpath('.//tr')
                for row in rows[1:]:
                    cols = row.xpath('.//td')
                    if len(cols) == 3:
                        self.nested_table_data.append({
                            self.case_service['date']: cols[0].text_content().strip() or "NA",
                            self.case_service['description']: cols[1].text_content().strip() or "NA",
                            self.case_service['situation']: cols[2].text_content().strip() or "NA",
                        })
        if not self.nested_table_data:
            self.nested_table_data = [self.empty_case_status_details()]

    def empty_case_status_details(self):
        return {
            self.case_service['date']: "NA",
            self.case_service['description']: "NA",
            self.case_service['situation']: "NA"
        }

    def get_hearing_details(self, tree):
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
            self.case_service['heading_date']: "NA",
            self.case_service['judges']: "NA",
            self.case_service['case_status']: "NA",
            self.case_service['judgments']: "NA"
        }