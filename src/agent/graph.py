"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict, TypedDict
import os
import requests
from agent_functions.extracting_info import get_extracted_information
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from langchain.chat_models import init_chat_model
from pydantic import BaseModel,Field
from tools.youtube import search_youtube_videos
from tools.human_assistant import human_assistant
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.memory import InMemorySaver
import redis


url = "https://api.geoapify.com/v2/places?categories=healthcare.hospital,healthcare&filter=circle:3.3923165374758533,6.542001055294039,5000&bias=proximity:3.3923165374758533,6.542001055294039&limit=20&apiKey=8afc9b32319e44e584ff990567aac9ec"

llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
os.environ["LANGSMITH_TRACING"] = "true"

def add_symptoms(left,right):
    left = right
    return left

def add_link(left,right):
    left = left+right
    return left[:-6:-1]


@dataclass
class ContextSchema(TypedDict):
    picked: bool = False
    extracted : bool = False


class State(TypedDict):
    messages:Annotated[list,add_messages]
    report: dict
    symptoms: Annotated[set[str],add_symptoms]
    youtube_link : Annotated[list,add_link]
    user_id:str

from typing import Optional,List,Set
class Person(BaseModel):
    situation : str = Field(default='Emergency',description='The urgency of the situation : Emergency or Non-Emergency or non-medical if it is non related to medical situation')
    age : Optional[str] = Field(default=None,description='Based on the age in the given information classify them as pediatric,adult,geriatric')
    gender : Optional[str] = Field(default=None,description='The gender of the accident victim be it male or female')
    surgical_status : Optional[str] = Field(default=None,description=' Preoperative or Post operative or any name for the Surgical Status if no status can be infered')
    trauma_name : Optional[List[str]] = Field(default=None,description='Using the message,Classify into one or more of the trauma categories.e.g Penetrating Trauma')
    trauma_description : Optional[str] = Field(default=None,description=' A very short description of the situation in less than 100 characters')
    physicians : Optional[List[str]] = Field(default=None,description='a LIST of specially trained surgeons who are responsible for assessing, managing, and performing surgery when necessary on patients who have sustained the stated traumatic injuries')
    symptoms : Optional[Set[str]] = Field(default=None,description='Using the message , kindly state out atleast 5 possible observable symptoms that are likely to be a result of the medical situation')
    youtube_keywords : Optional[List[str]] = Field(default=None,description='Using the message , kindly state out emergency-related keywords that we can use to query the youtube API in first_aid_procedures format, always including one CPR-related keywords.')


class Data(BaseModel):
    people:List[Person]



def extraction(state:State,runtime: Runtime[ContextSchema]):
    if not runtime.context['picked']:
        prompt_template = ChatPromptTemplate([('system',
        "You will be given a message describing a possible medical situation."
        "Analyze the message and return a JSON object with the specified fields."
        "For 'Situation', classify as 'Emergency', 'Non-Emergency', or 'non-medical' if unrelated to a medical condition."
        "For 'Age', classify as 'Pediatric', 'Adult', or 'Geriatric' based on provided details, or 'Not Stated' if age cannot be inferred."
        "For 'Gender', infer gender from context (e.g., 'daughter', 'girl' → 'Female') or return 'Not Stated' if it cannot be inferred."
        "For 'Surgical Status', classify as 'Preoperative', 'Postoperative', or another surgical status if stated, otherwise return 'Not Stated'."
        "For 'Trauma Name', classify into a trauma category (e.g., 'Penetrating Trauma')."
        "For 'Trauma Description', provide a concise description of the traumatic event in under 100 characters."
        "For 'Physicians', list the specialized surgeons responsible for assessing, managing, and performing surgery for the identified trauma."
        "For 'Symptoms', provide at least 10 possible observable symptoms in Python set format."
        "For 'FirstAid_searchwords', list 7–10 emergency-related keywords that we can use to query the youtube API in 'first_aid_procedures' format, always including one CPR-related keywords."
        "If the message does not describe a medical-related condition, return exactly 'non medical related condition'."
                            ),
        ('human','{text}')])
        structured_llm = llm.with_structured_output(schema=Data)
        prompt = prompt_template.invoke({'text':state['messages'][-1].content})
        response = structured_llm.invoke(prompt)
        structured_response = json.loads(response.json())['people'][-1]
        symptoms = set(structured_response['symptoms'])
        keys_to_get = ['situation','age','gender','surgical_status','trauma_name','trauma_description','physicians']
        report = {key: structured_response[key] for key in keys_to_get if key in structured_response}
        reformatted_report ={key:(','.join(value) if type(value) is list else value) for key,value in report.items()}
        return {'report':reformatted_report,'symptoms':symptoms}



def hospital_request(state:State):
    response = requests.get(url)
    r = redis.Redis(host='localhost', port=6379,decode_responses=True)
    for i in response.json()['features']:
        if 'name' in i['properties'].keys():
            stream_id = i['properties']['place_id'][:8]
            report_to_be_sent = state['report']
            report_to_be_sent.update({'user':state['user_id']})
            print(report_to_be_sent)
            # print()
            r.xadd(stream_id,report_to_be_sent)
    return {}
    # deadline = time.time() + 120
    # while time.time() < deadline:
    #     msgs = r.xread({state["user_id"]: "$"}, block=2000)  # wait 2s
    #     if msgs:
    #         for stream, events in msgs:
    #             for msg_id, data in events:
    #                 if data["request_id"] == request_id:  # filter only my request
    #                     print("Got response:", data)
    #                     break
        

def chatbot(state:State,runtime: Runtime[ContextSchema]):
    first_aid_prompt_template = ChatPromptTemplate([('system',
                   " You are First Aid Bot Bot, an automated service to help with medical emergency till professional help arrives.i want you to follow the steps below "
                   "Step 1 : You will be given a set of symptoms - {symptoms},and also the user emergency message {query}, and also information relevant to the situation."
                   "Step 2 : Then you say this - `Thank you for sharing that, the information has been sent to the nearest hospital requiring their assitant."
                   "I will provide you with guidance while we wait for professional assistance.Remember, your safety is our top priority."
                                                   " Now, let's focus on getting you the first aid medical assistance you need - `.`"
           " Step 3 : Carefully, Start a First aid Measure according to the symptoms {symptoms}, you can use this {information} to guide yourself, the user will need to take in other to keep the Medical Situation from Escalating, ensure to take note of the following : "
                       " a. Ensure to tell them that they can always ask for further guidance from you if a particular First Aid Measure isn't understood by them ."
                       " b. Ensure You respond in a short, very conversational friendly style."
            "            c. Ensure You return a first aid guidance according to the medical emergency in numerical order."
            "Step 4 : During a point in your conversation, if a user ask for further guidance on what to do about a particular first a step, i want you to do the following below : "
            "            i. Ensure that your textual descriptions are clear, concise, and easy to understand. Use simple language and provide step-by-step instructions."
            "            ii.)Keep in mind that users may have different levels of medical knowledge and understanding.it's crucial to gauge user comprehension and offer additional clarification if needed."
            "            iii.) you can ask the user if they want a video that gives an example, if they yes, kindly  use the `youtube_query_search` tool with a query string of the emergency procedure the user requested."
            "Step 5 : If the user ask for a video, demonstration or anything similar to visual analogy to a particular step, use the `youtube_query_search` tool with a query string of the emergency procedure the user requested."
                    )

                                                    ])


    if runtime.context['picked']:
        if runtime.context['extracted']:
            first_aid_prompt = first_aid_prompt_template.invoke({'query':state['messages'][0].content,'symptoms':state['symptoms'],'information':''})#the extracted information
        elif not runtime.context['extracted']:
        # making sure extract does not run twice
            extract = get_extracted_information()
            extracted_information =  extract.invoke(state)#get_extracted_info
            first_aid_prompt = first_aid_prompt_template.invoke({'query':state['messages'][0].content,'symptoms':state['symptoms'],'information':extracted_information})#the extracted information
            ##############################
        messages = [first_aid_prompt.messages[0]]+state['messages']
        message = llm_with_tools.invoke(messages)
        assert(len(message.tool_calls) <= 1)
    else:
        message = llm_with_tools.invoke(f'Ask user to pick between the symptoms listed in {state["symptoms"]},')
        print('yesssssssssssssssssssss')
        assert(len(message.tool_calls) <= 1)
    return {'messages':message}

tools = [human_assistant,search_youtube_videos]
llm_with_tools = llm.bind_tools(tools)

# Define the graph

builder = StateGraph(State,context_schema=ContextSchema)
builder.add_node(extraction)
builder.add_node(hospital_request)
builder.add_node(chatbot)
tool_node = ToolNode(tools=tools)
builder.add_node("tools", tool_node)
builder.add_edge(START,'extraction')
builder.add_edge('extraction','hospital_request')
builder.add_edge('extraction','chatbot')
builder.add_edge('tools','chatbot')
builder.add_edge('hospital_request',END)
builder.add_conditional_edges("chatbot", tools_condition)
# add a conditional edge
# builder.add_edge('human_assistant',END)
# memory = InMemorySaver()
graph = builder.compile()

