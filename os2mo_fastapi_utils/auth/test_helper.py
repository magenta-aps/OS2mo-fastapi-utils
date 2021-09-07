# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import List
import unittest.mock

from fastapi.routing import APIRoute
from starlette.routing import BaseRoute


class TestServiceAuth(unittest.TestCase):
    """
    Test that OIDC auth is enabled on all endpoints except from those
    specified in an explicit exclude list (see the NO_AUTH_ENDPOINTS below).

    Override the no_auth_endpoints, all_routes and auth_coroutine in the
    setUp method.
    """

    def setUp(self) -> None:

        # No fancy logic (for security reasons) to set the excluded endpoints -
        # all excluded endpoints must be explicitly specified in the list

        # E.g. ('/health/', '/version/',...)
        self.no_auth_endpoints: List[str] = []

        # E.g. main.app.routes
        self.all_routes: List[BaseRoute] = []

        # E.g. main.auth.oidc.auth (in LoRa)
        self.auth_coroutine = None

    def lookup_auth_dependency(self, route: APIRoute):
        # Check if auth dependency exists
        return any(d.dependency == self.auth_coroutine for d in route.dependencies)

    def test_assert_route_and_auth_values_are_set(self):
        # Make sure that these have been set in the downstream code
        assert self.all_routes
        assert self.auth_coroutine

    def test_ensure_endpoints_depend_on_oidc_auth_function(self):
        # A little risky since we should avoid "logic" in the test code!
        # (so direct auth "requests" tests added in class below)

        # Loop through all FastAPI routes (except the ones from the above
        # exclude list) and make sure they depend (via fastapi.Depends) on the
        # auth function in the mora.auth.keycloak.oidc sub-module.

        # Skip the starlette.routing.Route's (defined by the framework)
        routes = filter(
            lambda route: isinstance(route, APIRoute),
            self.all_routes
        )
        # Only check endpoints not in the NO_AUTH_ENDPOINTS list
        routes = filter(
            lambda route: route.path not in self.no_auth_endpoints,
            routes
        )
        for route in routes:
            has_auth = self.lookup_auth_dependency(route)
            assert has_auth, f"Route not protected: {route.path}"

    def test_ensure_no_auth_endpoints_do_not_depend_on_auth_function(self):
        no_auth_routes = filter(
            lambda route: route.path in self.no_auth_endpoints,
            self.all_routes
        )
        for route in no_auth_routes:
            has_auth = self.lookup_auth_dependency(route)
            assert not has_auth, f"Route protected: {route.path}"
