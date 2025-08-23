from googleapiclient.discovery import build
from datetime import timedelta
from typing import Annotated
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command
import isodate  # For parsing ISO 8601 durations
import os
@tool('search_youtube_videos',parse_docstring=True)
def search_youtube_videos(query:Annotated[str,'query string of the emergency procedure the user requested'],
                          max_results:Annotated[int,' Max videos to return'],
                          tool_call_id: Annotated[str, InjectedToolCallId]) -> str:
    """
    Search YouTube videos with exact duration filtering.

    Args:
        query (str): Search term
        max_results (int): Max videos to return
    """
    api_key = os.environ.get("YOUTUBE_API_KEY")
    youtube = build('youtube', 'v3', developerKey=api_key)

    min_duration =1
    max_duration=5
    max_results  = 10
    # Initial search (without duration filter)
    search_response = youtube.search().list(q=query,part="id,snippet",type="video",maxResults=max_results * 2,order="relevance").execute()
    # Get video IDs for detailed lookup
    video_ids = [item['id']['videoId'] for item in search_response['items']]

    # Get detailed duration info
    videos_response = youtube.videos().list(id=','.join(video_ids),part="contentDetails,statistics,snippet").execute()

    # Process results with duration filtering
    valid_videos = []
    for video in videos_response['items']:
        duration = isodate.parse_duration(video['contentDetails']['duration'])
        minutes = duration.total_seconds() / 60

        # Check duration constraints
        duration_ok = True
        if min_duration is not None and minutes < min_duration:
            duration_ok = False
        if max_duration is not None and minutes > max_duration:
            duration_ok = False

        if duration_ok:
            valid_videos.append({'title': video['snippet']['title'],'url': f"https://youtu.be/{video['id']}",'duration': str(timedelta(minutes=minutes))[:-3],'views': int(video['statistics'].get('viewCount', 0))})
            if len(valid_videos) >= max_results:
                break
    youtube_vids  = [{'title':video['title'],'url':video['url']} for idx, video in enumerate(valid_videos, 1)]
    if len(youtube_vids)>0:
        response = 'The video has been uploaded to the youtube link state, ask user to check it.'
    else:
        response = 'No video found, kindly describe it better for the user'

    state_update = {'youtube_link':youtube_vids,'messages':[ToolMessage(response, tool_call_id=tool_call_id)]}
    return Command(update=state_update)

