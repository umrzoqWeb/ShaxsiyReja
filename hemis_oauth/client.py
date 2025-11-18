# hemis_oauth/client.py
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode
from django.conf import settings

class HemisOAuthClient:
    def __init__(self, profile: str):
        cfg = getattr(settings, "HEMIS_OAUTH", {})
        self.profile = profile.lower()
        if self.profile not in {"employee", "student"}:
            raise ValueError("Profile noto‘g‘ri")

        base = "https://hemis.zarmeduniver.com" if self.profile == "employee" else "https://student.zarmeduniver.com"

        self.client_id = cfg["CLIENT_ID"]
        self.client_secret = cfg["CLIENT_SECRET"]
        self.user_fields = cfg.get(
            "USER_FIELDS",
            "id,uuid,type,name,login,picture,email,university_id,phone"
        )

        self.authorize_url = f"{base}/oauth/authorize"
        self.token_url = f"{base}/oauth/access-token"
        self.userinfo_url = f"{base}/oauth/api/user"

        # HEMIS panelida ko‘rsatilgan yagona callback
        self.redirect_uri = settings.SITE_BASE_URL.rstrip("/") + "/oauth/hemis/callback/"

    def build_authorize_url(self, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
        }
        return f"{self.authorize_url}?{urlencode(params)}"

    def fetch_token(self, code: str) -> dict:
        data = {
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": code,
        }
        resp = requests.post(
            self.token_url,
            data=data,
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    def fetch_userinfo(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"fields": self.user_fields}
        resp = requests.get(self.userinfo_url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()
