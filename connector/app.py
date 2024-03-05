import logging

from connexion.exceptions import Unauthorized
from flask import abort, request, current_app as app

from connector import create_app, UpstreamProviderError, provider

logger = logging.getLogger(__name__)
AUTHORIZATION_HEADER = "Authorization"
BEARER_PREFIX = "Bearer "

app = create_app

def get_access_token() -> str | None:
    authorization_header = request.headers.get(AUTHORIZATION_HEADER, "")
    if authorization_header.startswith(BEARER_PREFIX):
        return authorization_header.removeprefix(BEARER_PREFIX)
    return None

def search(body):
    with app.app_context():
        try:
            data = provider.search(body["query"], get_access_token())
        except UpstreamProviderError as error:
            logger.error(f"Upstream connector error: {error.message}")
            abort(502, error.message)
        except AssertionError as error:
            logger.error(f"GDrive config error: {error}")
            abort(502, f"GDrive config error: {error}")

        return {"results": data}, 200, {"X-Connector-Id": app.config.get("APP_ID")}


def apikey_auth(token):
    with app.app_context():
        api_key = app.config.get("CONNECTOR_API_KEY", "")
        if api_key != "" and token != api_key:
            raise Unauthorized()
        # successfully authenticated
        return {}
