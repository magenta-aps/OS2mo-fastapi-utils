<!--
SPDX-FileCopyrightText: Magenta ApS

SPDX-License-Identifier: MPL-2.0
-->

# OS2MO-FastAPI-Utils

Utility library with various reusable FastAPI components.


## Instrumentation Usage
Install into your project using `pip`:
```
pip install os2mo-fastapi-utils
```

Then import it inside a Python file:
```
from fastapi import FastAPI
from os2mo_fastapi_utils.tracing import setup_instrumentation

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

app = setup_instrumentation(app)
```


## Keycloak Autentication

The `auth` package in this module provides a Keycloak auth `Depends` coroutine
for FastAPI. Do (e.g.) the following to use this in FastAPI:
```
from fastapi import FastAPI, Depends
from structlog import get_logger

from os2mo_fastapi_utils.auth.exceptions import AuthenticationError
from os2mo_fastapi_utils.auth.oidc import get_auth_dependency
from os2mo_fastapi_utils.auth.oidc import get_auth_exception_handler
from myproject.models import MyToken

logger = get_logger()

auth = get_auth_dependency(
           host='keycloak',
           port=8081,
           realm='mo',
           token_url_path='service/token',
           token_model=MyToken
       )

app = FastAPI()
app.add_exception_handler(
    AuthenticationError,
    get_auth_exception_handler(logger)
)

@app.get("/")
async def root(token: Token = Depends(auth)):
    return {"message": "Hello World"}
```
