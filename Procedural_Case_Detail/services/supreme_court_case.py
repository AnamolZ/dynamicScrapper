from services.case_fetcher import CaseFetcher
from services.case_parser import CaseParser
from services.data_saver import DataSaver
import yaml

class SupremeCourtCase:
    def __init__(self, reg_no):
        self.reg_no = reg_no
        self.case_fetcher = CaseFetcher(reg_no)
        self.case_parser = CaseParser()

        with open('config.yml', 'r', encoding='utf-8') as file:
            self.case_service = yaml.safe_load(file) 

    def process_case(self):
        case_detail_url = self.case_fetcher.fetch_case_detail_url()
        if case_detail_url:
            self.case_parser.parse_case_info(case_detail_url)
            data_saver = DataSaver(
                self.case_parser.case_details,
                self.case_parser.issue_details,
                self.case_parser.date_details,
                self.case_parser.nested_table_data,
                self.case_parser.hearing_details,
                self.case_service
            )
            data_saver.save_data()
