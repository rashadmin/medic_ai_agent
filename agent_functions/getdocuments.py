from bs4 import BeautifulSoup
import requests
class get_documents:
    def __init__(self,ai_response,emergencies):
        self.ai_response = ai_response
        self.emergencies = emergencies

    def get_first_aid_links(self):
        # ai will be provided with current medical emergencies first aid list for both website. if it decides to go with either one in the website it will return a dict e.g
        link_url = {'Mayo_Clinic':'https://www.mayoclinic.org/first-aid' ,'Red_Cross':'https://www.redcross.org/take-a-class/resources/learn-first-aid/'}
        temp_rag_doc = []

        # so we check based on the list:
        for source,emergency in self.ai_response.dict()['firstaid'][0].items():
            if len(emergency)!=0:
                print(emergency)
                temp_rag_doc.extend([f'{link_url[source]}{self.emergencies[source][link]}' for link in emergency])
        return temp_rag_doc
    def extract_content(self,url):

    # Send HTTP GET request with headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise error for bad status codes

            # Get HTML content
            html_content = response.text
            # print(url)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            exit()


        # Assuming `html_content` contains your HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        if 'mayoclinic' in url:
            elements = soup.find(id="main-content")
            content = elements.text.replace('\n','').replace('\t','').replace('\r','')
            content = content.split('From Mayo Clinic to your inbox')[0]
            return content
        elif 'redcross' in url:
            elements = soup.find(id="primary")
            content = elements.text.replace('\n','').replace('\t','').replace('\r','')
            content = content.split('Help Save Lives with an American Red Cross Class')[0]
            return content
    def extract_contents(self):
        link_list = self.get_first_aid_links()
        # document = '\n'.join([i for i in link_list])
        document = '\n'.join([self.extract_content(i) for i in link_list])
        return document
