# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

import jwt.exceptions
from fastapi import Depends
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from os2mo_fastapi_utils.auth.exceptions import AuthenticationError
from os2mo_fastapi_utils.auth.models import Token

TokenModel = TypeVar("TokenModel", bound=Token)


def get_auth_dependency(
    host: str,
    port: int,
    realm: str,
    token_url_path: str,
    token_model: Type[TokenModel],
    http_schema: str = "http",
    alg: str = "RS256",
    verify_audience: bool = True,
    audience: Union[str, List[str], None] = None,
):
    # URI for obtaining JSON Web Key Set (JWKS), i.e. the public Keycloak key
    JWKS_URI = (
        f"{http_schema}://{host}:{port}"
        f"/auth/realms/{realm}/protocol/openid-connect/certs"
    )

    # JWKS client for fetching and caching JWKS
    jwks_client = jwt.PyJWKClient(JWKS_URI)

    # For getting and parsing the Authorization header
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url_path)

    async def keycloak_auth(token: str = Depends(oauth2_scheme)) -> TokenModel:
        """
        Ensure the caller has a valid OIDC token, i.e. that the Authorization
        header is set with a valid bearer token.

        :param token: encoded Keycloak token
        :return: selected JSON values from the Keycloak token

        **Example return value**

        .. sourcecode:: json

            {
                "acr": "1",
                "allowed-origins": ["http://localhost:5001"],
                "azp": "mo",
                "email": "bruce@kung.fu",
                "email_verified": false,
                "exp": 1621779689,
                "family_name": "Lee",
                "given_name": "Bruce",
                "iat": 1621779389,
                "iss": "http://localhost:8081/auth/realms/mo",
                "jti": "25dbb58d-b3cb-4880-8b51-8b92ada4528a",
                "name": "Bruce Lee",
                "preferred_username": "bruce",
                "realm_access": {
                    "roles": [
                      "admin"
                  ]
                },
                "scope": "email profile",
                "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
                "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
                "typ": "Bearer",
                "uuid": "99e7b256-7dfa-4ee8-95c6-e3abe82e236a"
            }

        """

        try:
            # Get the public signing key from Keycloak. The JWKS client uses an
            # lru_cache, so it will not make an HTTP request to Keycloak each time
            # get_signing_key_from_jwt() is called.

            signing = jwks_client.get_signing_key_from_jwt(token)

            # The jwt.decode() method raises an exception (e.g.
            # InvalidSignatureError, ExpiredSignatureError,...) in case the OIDC
            # token is invalid. These exceptions will be caught by the
            # auth_exception_handler below which is used by the FastAPI app.

            # The audience verification can be disabled (aud
            # claim in the token) when all services in the stack trust
            # each other
            # (see https://www.keycloak.org/docs/latest/server_admin/index.html#_audience)
            decoded_token: dict = jwt.decode(
                token,
                signing.key,
                algorithms=[alg],
                audience=audience,
                options={"verify_aud": verify_audience},
                leeway=5,
            )

            return token_model.parse_obj(decoded_token)

        except Exception as err:
            raise AuthenticationError(err)

    return keycloak_auth


def get_auth_exception_handler(logger: Any):
    """
    Returns an authentication exception handler to be used by the FastAPI
    app object

    :param logger: any logger for logging auth errors
    """

    def authentication_exception_handler(
        request: Request, err: AuthenticationError
    ) -> JSONResponse:
        if err.is_client_side_error():
            logger.exception("Client side authentication error", exc_info=err)
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"status": "Unauthorized", "msg": str(err.exc)},
            )

        logger.exception("Problem communicating with the Keycloak server", exc_info=err)

        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": "A server side authentication error occurred"},
        )

    return authentication_exception_handler
