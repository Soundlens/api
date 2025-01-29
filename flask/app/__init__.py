"""
Welcome to the documentation for the soundlens API!

## Introduction
soundlens-db ia web API for creating soundlenss.
as it provides a a back end that you can .

## Authentication
The authentication for this API is based on *access* and *refresh*
tokens.
To obtain an access and refresh token pair, the User must send a `POST`
request to the `/api/tokens` endpoint, passing the username and password of
the user in a `Authorization` header, according to Token scheme.
The response includes the access and refresh tokens in the body.
For added security the refresh token is also returned in a secure cookie.
Most endpoints in this API are authenticated with the access token, passed
in the `Authorization` header, using the `Bearer` scheme.
Access tokens are valid for 15 minutes (by default) from the time they are
issued.
When the access token is expired, the User can renew it using the refresh token. For this, the User must send a `PUT` request to the
`/api/tokens` endpoint, passing the expired access token in the body of the
request, and the refresh token either in the body, or through the secure cookie
sent when the tokens were requested.
The response to this request will include a new pair of tokens. Refresh tokens have a default validity period of 7 days,
and can only be used to renew the access token they were returned with.
After that the refersh token is expired.
An attempt to use a refresh token more than once is considered a possible attack, will 
and will cause all existing tokens for the user to be revoked immediately as a
mitigation measure.
 
### Authentication Error 
| Status Code | Error Name  | Description |
| - | - | - |
| `401` | `Unauthorized!` | access_token_expiration ended and User can use refresh_token to have a new pair. Response has a refresh token url |
| `401` | `Unauthorized!` | the user is unauthorized to to access the page, needs either to login . |
 
 
### Environment Variables 
| Environment Variable | Default | Description |
| - | - | - |
| `SECRET_KEY` | `top-secret!` | A secret key used when signing tokens. |
| `DATABASE_URL`  | `sqlite:///db.sqlite`.
| `ACCESS_TOKEN_MINUTES` | `15` | The number of minutes an access token is valid for. |
| `REFRESH_TOKEN_DAYS` | `7` | The number of days a refresh token is valid for. |
| `REFRESH_TOKEN_IN_COOKIE` | `yes` | Whether to return the refresh token in a secure cookie. |
| `REFRESH_TOKEN_IN_BODY' | `yes` | Whether to return the refresh token in the response body. |



"""

from app.main import (
    create_app,
    db,
    ma,
    celery,
    bootstrap_app,
    metadata,
)  # noqa
