# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from fastapi.routing import APIRoute


def lookup_auth_dependency(route, auth_coro):
    # Check if auth dependency exists
    return any(d.dependency == auth_coro for d in route.dependencies)


def ensure_endpoints_depend_on_oidc_auth_function(
    all_routes, no_auth_endpoints, auth_coro
):
    # A little risky since we should avoid "logic" in the test code!
    # (so direct auth "requests" tests should also be added)

    # Loop through all FastAPI routes (except the ones from the above
    # exclude list) and make sure they depend (via fastapi.Depends) on the
    # auth coroutine.

    # Skip the starlette.routing.Route's (defined by the framework)
    routes = filter(lambda _route: isinstance(_route, APIRoute), all_routes)
    # Only check endpoints not in the NO_AUTH_ENDPOINTS list
    routes = filter(lambda _route: _route.path not in no_auth_endpoints, routes)

    # Make sure that routes are defined
    assert list(routes)

    for route in routes:
        has_auth = lookup_auth_dependency(route, auth_coro)
        assert has_auth, f"Route not protected: {route.path}"


def ensure_no_auth_endpoints_do_not_depend_on_auth_function(
    all_routes, no_auth_endpoints, auth_coro
):
    no_auth_routes = filter(lambda _route: _route.path in no_auth_endpoints, all_routes)
    for route in no_auth_routes:
        has_auth = lookup_auth_dependency(route, auth_coro)
        assert not has_auth, f"Route protected: {route.path}"
