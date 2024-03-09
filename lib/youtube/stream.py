import os
import datetime
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

APP_TOKEN_FILE = "youtube_streamer/youtube_secret.json"
USER_TOKEN_FILE = "youtube_streamer/user_token.json"
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
]

def set_broadcast_thumbnail(youtube, broadcast_id, thumbnail):
    youtube.thumbnails().set(
        videoId=broadcast_id,
        media_body=thumbnail
    ).execute()
    print("Thumbnail successfully set for the broadcast.")

def get_broadcast_info(youtube, broadcast_id):
    request = youtube.liveBroadcasts().list(
        part='snippet,contentDetails,status',
        id=broadcast_id
    )

    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]
    else:
        return None

def insert_broadcast(youtube, title, description, privacyStatus="private"):
    scheduled_start_time = datetime.datetime.utcnow().isoformat()
    insert_broadcast_response = youtube.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body=dict(
            snippet=dict(
                title=title,
                description=description,
                scheduledStartTime=scheduled_start_time
            ),
            status=dict(
                privacyStatus=privacyStatus
            ),
            contentDetails=dict(
                enableAutoStart=True,
                enableAutoStop=True,
            )
        )
    ).execute()

    snippet = insert_broadcast_response["snippet"]

    print("Broadcast created with title: %s" % snippet["title"])
    print("Scheduled start time: %s" % snippet["scheduledStartTime"])
    return insert_broadcast_response


def insert_stream(youtube, title, description):
    insert_stream_response = youtube.liveStreams().insert(
        part="snippet,cdn",
        body=dict(
            snippet=dict(
                title=title,
                description=description,
            ),
            cdn=dict(
                format="1080p",
                ingestionType="rtmp",
                resolution="variable",
                frameRate="variable"
            )
        )
    ).execute()
    snippet = insert_stream_response["snippet"]
    print("Stream created with title: %s" % snippet["title"])
    return insert_stream_response


def bind_broadcast_and_stream(youtube, broadcast_id, stream_id):
    youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_id
    ).execute()

    print("Broadcast and Stream bound")


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

def create_stream(title, description, thumbnail, privacyStatus="private"):
    service = get_service()
    insert_broadcast_response = insert_broadcast(service, title, description, privacyStatus)
    broadcast_id = insert_broadcast_response["id"]
    set_broadcast_thumbnail(service, broadcast_id, thumbnail)
    insert_stream_response = insert_stream(service, title, description)
    stream_id = insert_stream_response["id"]
    bind_broadcast_and_stream(service, broadcast_id, stream_id)
    #print(insert_stream_response)
    #pretty_json = json.dumps(insert_stream_response, indent=4)
    #print("====================\n",pretty_json)
    if 'cdn' not in insert_stream_response or 'ingestionInfo' not in insert_stream_response['cdn']:
        print("Bad insert stream response")
        pretty_json = json.dumps(insert_stream_response, indent=4)
        return None
    stream_key = insert_stream_response['cdn']['ingestionInfo']['streamName']
    ingestion_address = insert_stream_response['cdn']['ingestionInfo']['ingestionAddress']
    ingestion = ingestion_address + '/' + stream_key
    return ingestion
    