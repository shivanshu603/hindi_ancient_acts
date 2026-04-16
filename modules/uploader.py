import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class YouTubeUploader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        self.credentials = None
        self.service = None

    def authenticate(self):
        """Authenticate using saved token or refresh"""
        token_path = 'token.pickle'

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                print("❌ YouTube OAuth token missing. Please run setup again.")
                return False

        self.service = build('youtube', 'v3', credentials=self.credentials)
        return True

    def upload(self, video_path, title, description, tags=None, privacy="public"):
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return None

        if not self.authenticate():
            return None

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or ["ai", "story", "shorts", "cinematic"],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

        try:
            request = self.service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            print("📤 Uploading video to YouTube... (this may take 30-60 seconds)")
            response = request.execute()

            video_id = response['id']
            print(f"✅ Upload Successful!")
            print(f"🔗 https://youtu.be/{video_id}")
            return video_id

        except Exception as e:
            print(f"❌ YouTube Upload Failed: {e}")
            return None
