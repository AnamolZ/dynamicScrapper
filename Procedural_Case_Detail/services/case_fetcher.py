import requests
from bs4 import BeautifulSoup

class CaseFetcher:
    def __init__(self, reg_no):
        self.reg_no = reg_no

    def fetch_case_detail_url(self):
        url = "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details"
        data = {'regno': self.reg_no, 'mode': 'show', 'list': 'list'}
        response = requests.post(url, data=data, verify=False)
        
        if response.ok:
            soup = BeautifulSoup(response.content, 'html.parser')
            anchor_tag = soup.find('a', href=lambda x: 'sys.php?d=reports' in x)
            if anchor_tag:
                return f"https://supremecourt.gov.np/lic/{anchor_tag['href'].replace('&amp;', '&')}"
        return None
