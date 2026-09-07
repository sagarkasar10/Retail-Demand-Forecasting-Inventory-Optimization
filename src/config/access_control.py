import os
from typing import Dict, List


ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "admin": [
        "view_dashboard",
        "view_forecasts",
        "view_inventory",
        "run_scenarios",
        "export_reports",
        "manage_users",
    ],
    "manager": [
        "view_dashboard",
        "view_forecasts",
        "view_inventory",
        "run_scenarios",
        "export_reports",
    ],
    "analyst": [
        "view_dashboard",
        "view_forecasts",
        "view_inventory",
        "run_scenarios",
    ],
    "viewer": [
        "view_dashboard",
        "view_forecasts",
        "view_inventory",
    ],
}


def get_current_role() -> str:
    """Get the current application role."""

    role = os.getenv(
        "APP_USER_ROLE",
        "viewer",
    ).lower()

    if role not in ROLE_PERMISSIONS:
        return "viewer"

    return role


def get_role_permissions(
    role: str,
) -> List[str]:
    """Return permissions assigned to a role."""

    return ROLE_PERMISSIONS.get(
        role.lower(),
        [],
    )


def has_permission(
    permission: str,
    role: str | None = None,
) -> bool:
    """Check whether a role has a specific permission."""

    if role is None:
        role = get_current_role()

    permissions = get_role_permissions(
        role
    )

    return permission in permissions


def require_permission(
    permission: str,
) -> bool:
    """Validate access for the current user role."""

    return has_permission(
        permission=permission
    )


def get_access_summary() -> Dict[str, object]:
    """Return access control information."""

    current_role = get_current_role()

    return {
        "role": current_role,
        "permissions": get_role_permissions(
            current_role
        ),
    }