import json
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command,interrupt
from typing import Annotated,List
@tool
def human_assistant(symptoms:List[str],tool_call_id: Annotated[str, InjectedToolCallId])-> str:
    ''' It request for users to select the symptoms that can be observe after the symptoms state has been populated'''
    human_response = interrupt({'question':'Select the symptoms you can observe :','symptoms':symptoms})
    print(human_response)
    # print('qwertyuiop')
    if len(human_response['symptoms']) > 0:
        verified_symptoms = human_response.get("symptoms", symptoms)
        picked = True
        response = f'User selected symptoms {verified_symptoms}'
    else:
        verified_symptoms = symptoms
        response  = f'User did not select symptoms {verified_symptoms}'
    state_update = {'symptoms':verified_symptoms,'picked':picked,'messages':[ToolMessage(response, tool_call_id=tool_call_id)]}
    return Command(update=state_update)