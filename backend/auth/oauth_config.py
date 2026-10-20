"""OAuth configuration for YouTube, Instagram, and LinkedIn."""

from config import settings

OAUTH_CONFIGS = {
    "youtube": {
        "provider": "google",
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "redirect_uri": settings.google_redirect_uri,
        "scopes": [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
    },
    "instagram": {
        "provider": "meta",
        "client_id": settings.meta_client_id,
        "client_secret": settings.meta_client_secret,
        "authorize_url": "https://www.facebook.com/v19.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v19.0/oauth/access_token",
        "redirect_uri": settings.meta_redirect_uri,
        "scopes": [
            "instagram_basic",
            "instagram_content_publish",
            "pages_show_list",
            "pages_read_engagement",
        ],
    },
    "linkedin": {
        "provider": "linkedin",
        "client_id": settings.linkedin_client_id,
        "client_secret": settings.linkedin_client_secret,
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "redirect_uri": settings.linkedin_redirect_uri,
        "scopes": [
            "openid",
            "profile",
            "w_member_social",
        ],
    },
}
