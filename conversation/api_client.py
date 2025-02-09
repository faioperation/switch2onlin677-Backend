import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class MetaApiClient:
    def __init__(self):
        # WhatsApp always uses the general page token
        self.whatsapp_phone_number_id = getattr(settings, "META_WHATSAPP_PHONE_NUMBER_ID", "")

        # Platform-specific tokens
        self.fb_token = (
            getattr(settings, "META_FB_PAGE_ACCESS_TOKEN", "")
            or getattr(settings, "META_PAGE_ACCESS_TOKEN", "")
        )
        self.ig_token = (
            getattr(settings, "META_IG_PAGE_ACCESS_TOKEN", "")
            or getattr(settings, "META_PAGE_ACCESS_TOKEN", "")
        )
        # WhatsApp uses FB token (Cloud API uses page token or system token)
        self.whatsapp_token = (
            getattr(settings, "META_PAGE_ACCESS_TOKEN", "")
            or self.fb_token
        )

        # Legacy fallback
        self.page_access_token = getattr(settings, "META_PAGE_ACCESS_TOKEN", "")

    def get_token_for_platform(self, platform):
        """
        Returns the correct access token based on the messaging platform.

        IMPORTANT: Instagram Messaging (Messenger API for Instagram) uses the
        same Facebook Page Access Token as Messenger — NOT an IGA... token.
        The token just needs instagram_manage_messages permission.
        """
        from conversation.models import PlatformChoices
        if platform == PlatformChoices.INSTAGRAM:
            # Instagram Messaging uses the FB Page Access Token (EAA...) with
            # instagram_manage_messages permission — same endpoint, same token type.
            return self.fb_token
        elif platform == PlatformChoices.FACEBOOK:
            return self.fb_token
        else:  # whatsapp
            return self.whatsapp_token

    def get_headers(self, token=None):
        active_token = token or self.page_access_token
        if not active_token:
            return {}
        return {"Authorization": f"Bearer {active_token}"}

    def send_meta_request(self, url, payload, token=None):
        """
        Base method to send POST requests to Meta.
        Accepts an optional token override for platform-specific requests.
        """
        try:
            response = requests.post(url, json=payload, headers=self.get_headers(token))
            return response.status_code, response.json()
        except Exception as e:
            logger.error(f"Meta API Request Error: {str(e)}")
            return 500, {"error": str(e)}

    def fetch_user_profile(self, user_id, fields, token=None):
        """
        Fetches user profile data from Meta Graph API.
        For Facebook: user_id is the Page-Scoped User ID (PSID).
        For Instagram: user_id is the Instagram-Scoped User ID (IGSID).
        """
        url = f"https://graph.facebook.com/v25.0/{user_id}"
        active_token = token or self.page_access_token
        params = {
            "fields": fields,
            "access_token": active_token,
        }
        try:
            response = requests.get(url, params=params)
            logger.info(f"Profile fetch for {user_id}: status={response.status_code}")
            if response.status_code != 200:
                logger.error(f"Profile fetch failed: {response.text}")
            return response.status_code, response.json()
        except Exception as e:
            logger.error(f"Meta Profile Fetch Error: {str(e)}")
            return 500, {"error": str(e)}

    def get_media_info(self, media_id):
        """
        Gets the download URL for a given Meta Media ID.
        """
        url = f"https://graph.facebook.com/v25.0/{media_id}"
        params = {
            "access_token": self.whatsapp_token or self.page_access_token,
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"Meta Media Info Error: {response.status_code} - {response.text}")
            return response.status_code, response.json()
        except Exception as e:
            logger.error(f"Meta Media Info Exception: {str(e)}")
            return 500, {"error": str(e)}

    def download_media_content(self, url):
        """
        Downloads the raw media bytes from a Meta CDN URL.
        """
        try:
            response = requests.get(url, headers=self.get_headers(self.whatsapp_token), stream=True)
            return response
        except Exception as e:
            logger.error(f"Meta Media Download Error: {str(e)}")
            return None
