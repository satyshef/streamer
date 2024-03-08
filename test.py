import datetime
import json
import os
import threading
import time

#import cv2
import subprocess
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

APP_TOKEN_FILE = "./data/youtube_secret.json"
USER_TOKEN_FILE = "user_token.json"

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
]


def get_stream_info(stream_id):
    creds = get_creds_saved()
    service = build('youtube', 'v3', credentials=creds)

    request = service.liveBroadcasts().list(
        part='snippet,contentDetails,status',
        id=stream_id
    )

    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]
    else:
        return None


def get_creds_cons():
    # Create credentials via console flow
    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
    return flow.run_console()


def get_creds_saved():
    creds = None

    if os.path.exists(USER_TOKEN_FILE):
        # Load user credentials from a saved file
        creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Create new credentials via local server flow
            flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(USER_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_service():
    # Get YouTube API service using credentials
    creds = get_creds_saved()
    service = build('youtube', 'v3', credentials=creds)
    return service


def create_live_stream(title, description):
    service = get_service()
    scheduled_start_time = datetime.datetime.utcnow().isoformat()

    request = service.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": scheduled_start_time,
            },
            "status": {
                "privacyStatus": "private",
                "lifeCycleStatus": "ready",
                "recordingStatus": "notRecording",
                "selfDeclaredMadeForKids": False
            },
            "contentDetails": {
                "enableAutoStart": False
            }
        }
    )
    response = request.execute()
    return response['id']


def stream_video(video_path, stream_key):
    args = [
        '-re',
        '-i', video_path,
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-c:a', 'aac',
        '-f', 'flv',
        f'rtmp://a.rtmp.youtube.com/live2/{stream_key}'
    ]

    subprocess.run(['ffmpeg'] + args)


def get_scheduled_stream_info(stream_id):
    creds = get_creds_saved()
    service = build('youtube', 'v3', credentials=creds)

    request = service.liveBroadcasts().list(
        part='snippet,status',
        id=stream_id
    )

    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]
    else:
        return None



if __name__ == '__main__':
    print("** Hello, Azzrael_YT subscribers!!!\n")

    strId = create_live_stream("tittle", "description")
    pretty_json = json.dumps(get_scheduled_stream_info(strId), indent=4)

    print(pretty_json)

    # Stream video
    #video_path = "C:/Users/admin/PycharmProjects/pythonProject/video.mp4"  # Update this with your video file path
    #stream_key = 'dh9z-jtkx-wbq3-6wvp-2tac'  # Replace with your YouTube stream key
    #video_thread = threading.Thread(target=stream_video, args=(video_path, stream_key))
    #video_thread.start()