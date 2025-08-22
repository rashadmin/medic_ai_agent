from bs4 import BeautifulSoup
import requests



class get_first_aid_keywords:

    def __init__(self):
        self.emergencies = {'Mayo_Clinic':{},'Red_Cross':{}}

    def get_mayo_clinic_keywords(self):

        # Define the target URL
        url = "https://www.mayoclinic.org/first-aid"  # Replace with your actual URL

        # Send HTTP GET request with headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise error for bad status codes

            # Get HTML content
            html_content = response.text

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            exit()


        # Assuming `html_content` contains your HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # CSS selector for the parent <ol> (converted from XPath)
        selector = (
            "html > body > form > div:nth-of-type(6) > div:nth-of-type(1) "
            "> div:nth-of-type(4) > div:nth-of-type(2) > ol"
        )

        # Find the parent <ol> element
        parent_ol = soup.select_one(selector)

        mayo_clinic_hrefs = {}
        if parent_ol:
            # Find all <li> elements directly under the <ol>
            li_items = parent_ol.find_all('li', recursive=False)

            for li in li_items:
                # Find the <a> tag directly within the <li>
                a_tag = li.find('a')
                if a_tag and a_tag.has_attr('href'):
                    mayo_clinic_hrefs.update({a_tag.text:a_tag['href']})

            print(f"Found {len(mayo_clinic_hrefs)} hrefs:")
        else:
            print("Parent <ol> not found.")

        self.emergencies['Mayo_Clinic'].update(mayo_clinic_hrefs)

    def get_red_cross_keywords(self):
    # Define the target URL
        url = "https://www.redcross.org/take-a-class/resources/learn-first-aid"  # Replace with your actual URL

        # Send HTTP GET request with headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise error for bad status codes

            # Get HTML content
            html_content = response.text

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            exit()


        # Assuming `html_content` contains your HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # CSS selector for the parent <ul> of the target <li>
        selector = (
            "html > body > div:nth-of-type(1) > div:nth-of-type(2) > div:nth-of-type(3) "
            "> div:nth-of-type(1) > div:nth-of-type(3) > ul > li:nth-of-type(1) > ul"
        )

        # Find the parent <ul>
        # Find the parent <ol> element
        parent_ol = soup.select_one(selector)

        red_cross_hrefs = {}
        if parent_ol:
            # Find all <li> elements directly under the <ol>
            li_items = parent_ol.find_all('li', recursive=False)
            for li in li_items:
                # Find the <a> tag directly within the <li>
                a_tag = li.find('a')
                if a_tag and a_tag.has_attr('href'):
                    red_cross_hrefs.update({a_tag.text:a_tag['href'].split('/')[-1]})

            print(f"Found {len(red_cross_hrefs)} hrefs:")
        else:
            print("Parent <ol> not found.")
        self.emergencies['Red_Cross'].update(red_cross_hrefs)
    def get_keyword_dicts(self):
        self.get_mayo_clinic_keywords()
        self.get_red_cross_keywords()
        return self.emergencies