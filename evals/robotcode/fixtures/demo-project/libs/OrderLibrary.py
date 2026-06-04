"""A tiny in-memory order/login backend for the demo fixture.

No network, no database, no external services — every keyword resolves against
the dicts below, so the suite runs fully offline. These keywords back the
higher-level keywords in ``orders.resource``.
"""

_ORDERS = {
    "42": {"id": "42", "item": "widget", "qty": 3, "status": "shipped"},
    "7": {"id": "7", "item": "gadget", "qty": 1, "status": "pending"},
}

_USERS = {"alice": "correct horse"}


def get_login_response(username, password):
    """Return a login response dict for the given credentials.

    Correct credentials yield ``{"status": "ok", ...}``; anything else yields
    ``{"status": "error", "reason": "invalid credentials"}`` (it never raises,
    so a wrong password produces a *failed assertion* rather than an error).
    """
    if _USERS.get(username) == password:
        return {"status": "ok", "user": username, "token": "tok-123"}
    return {"status": "error", "reason": "invalid credentials"}


def get_order(order_id):
    """Return the order record for ``order_id``; raise if it does not exist."""
    order_id = str(order_id)
    if order_id not in _ORDERS:
        raise AssertionError(f"No order with id {order_id!r}")
    return dict(_ORDERS[order_id])


def get_order_status(order_id):
    """Return just the status string for ``order_id``."""
    return get_order(order_id)["status"]
