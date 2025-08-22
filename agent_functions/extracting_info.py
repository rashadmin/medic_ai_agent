from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel,Field
from agent_functions.firstaidkeywords import get_first_aid_keywords
from agent_functions.getdocuments import get_documents
from typing import Optional,List,Set
import os

# if not os.environ.get("GOOGLE_API_KEY"):
#   os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

from langchain.chat_models import init_chat_model

llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
emergencies = get_first_aid_keywords().get_keyword_dicts()

class FirstAidKeywords(BaseModel):
    Mayo_Clinic : Optional[List[str]] = Field(default=None,description='Using the message,Get the list of first aid key words in the mayo clinic dictionary that is similar to the user"s messages and the selected symptoms')
    Red_Cross : Optional[List[str]] = Field(default=None,description='Using the message,Get the list of first aid key words in the red cross dictionary that is similar to the user"s messages and the selected symptoms')

class FirstAidKeywordsList(BaseModel):
    firstaid:List[FirstAidKeywords]

class FirstAidInformation(BaseModel):
    first_aid_name : str = Field(description='Medical Emergency Name – The specific name of the condition (e.g., "Asthma attack").')
    symptoms: Optional[List[str]] = Field(default=None,description='Using the message,A list of symptoms in atmost 2-3 words per symptoms described in the HTML for that emergency.')
    instructions : Optional[List[str]] = Field(default=None,description='A list of Step-by-step instructions describing how to respond or provide first aid.')
class FirstAidInformationData(BaseModel):
    first_aids:List[FirstAidInformation]
class select_relevant_keyword:
    def __init__(self):
        self.prompt_template = ChatPromptTemplate([('system',
                                                "You will be given a message describing a possible medical situation {user_message} and you will be given a set of symptoms-{symptoms}"
                                                "You will also be given a list of mayo_clinic first_aid keyword - {mayo_clinic_keyword}"
                                                "You will also be given a list of red cross first_aid keyword - {red_cross_keyword}"
                                                "Analyze the message and the symptoms and return a dictionary object with the specified fields."
                                                "Mayo Clinic - which is going to contain at most 3 of the first aid keyword that best describes the user's message and the symptoms"
                                                "Red Cross - which is going to contain at most 3 of the first aid key word that best describes the user's message and the symptoms"
                                                "If one of the selected keyword is already present in the mayo clinic , do not repeat it in red cross dictionary and vice versa")
                                                            ,('human','{user_message}')     ])
    def invoke(self,state):
        keyword_prompt = self.prompt_template.invoke({'user_message':state['messages'][0].content,'symptoms':state['symptoms'],'mayo_clinic_keyword':emergencies['Mayo_Clinic'].keys(),'red_cross_keyword':emergencies['Red_Cross'].keys()})
        structured_llm = llm.with_structured_output(schema=FirstAidKeywordsList)
        selected_keywords = structured_llm.invoke(keyword_prompt)
        return selected_keywords
class get_extracted_information:
    def __init__(self):
        self.prompt_template = ChatPromptTemplate([('system',
            "You will be given HTML content describing one or more medical emergencies."
            "For each medical emergency mentioned, identify the emergency name such as 'Asthma Attack'."
            "Extract the symptoms listed for that emergency in atmost 2-3 words."
            "Extract the first aid procedure steps or instructions provided."
            "Return the results in JSON format with keys 'EmergencyName', 'Symptoms', and 'FirstAidProcedure'."
            "If multiple emergencies are present, output each as a separate object in a JSON array."
            "Ignore any unrelated content that is not part of a medical emergency description."),
            ('human','{html_content}')])

    def invoke(self,state):
        selection = select_relevant_keyword()
        selected_keywords = selection.invoke(state)
        documents =  get_documents(selected_keywords,emergencies).extract_contents()
        first_aid_prompt = self.prompt_template.invoke({'html_content':documents})
        structured_llm = llm.with_structured_output(schema=FirstAidInformationData)
        extracted_keywords = structured_llm.invoke(first_aid_prompt)
        return extracted_keywords