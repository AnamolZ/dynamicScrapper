import json
import os

class DataSaver:
    def __init__(self, case_details, issue_details, date_details, nested_table_data, hearing_details, case_service):
        self.case_details = case_details
        self.issue_details = issue_details
        self.date_details = date_details
        self.nested_table_data = nested_table_data
        self.hearing_details = hearing_details
        self.case_service = case_service

    def save_data(self):
        merged_data = {
            self.case_service['attachment_cases_details']: self.issue_details,
            self.case_service['date_details']: self.date_details,
            self.case_service['case_status_details']: self.nested_table_data,
            self.case_service['hearing_details']: self.hearing_details
        }
        file_path = 'procedural_case_detail.json'
        existing_data = []

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as json_file:
                    existing_data = json.load(json_file) or []
            except json.JSONDecodeError as e:
                print(f"Error reading JSON data: {e}")
        
        existing_data.insert(0, self.case_details)
        existing_data.insert(1, merged_data)
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
