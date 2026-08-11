from enum import Enum


class Role(str, Enum):
    CEO = "CEO"
    CTO = "CTO"
    ANALYST = "ANALYST"


# Metrics currently present in the structured database.
PUBLIC_METRICS = {
    "total_revenue",
    "iphone_revenue",
    "mac_revenue",
    "ipad_revenue",
    "services_revenue",
    "wearables_home_accessories_revenue",
}


# Restricted metrics can be expanded later when additional
# sensitive financial data is ingested.
RESTRICTED_METRICS = {
    "headcount",
    "compensation",
    "salary",
}


ROLE_PERMISSIONS = {
    Role.CEO: {
        "can_access_all": True,
    },
    Role.CTO: {
        "can_access_all": False,
        "allowed_metrics": PUBLIC_METRICS,
    },
    Role.ANALYST: {
        "can_access_all": False,
        "allowed_metrics": PUBLIC_METRICS,
    },
}


def normalize_role(role: str | Role) -> Role:
    if isinstance(role, Role):
        return role

    try:
        return Role(role.upper())
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid role: {role}")


def can_access_metric(
    role: str | Role,
    metric: str,
) -> bool:

    normalized_role = normalize_role(role)

    permissions = ROLE_PERMISSIONS[normalized_role]

    if permissions.get("can_access_all", False):
        return True

    return metric in permissions.get(
        "allowed_metrics",
        set(),
    )


def get_allowed_metrics(
    role: str | Role,
) -> set[str]:

    normalized_role = normalize_role(role)

    permissions = ROLE_PERMISSIONS[normalized_role]

    if permissions.get("can_access_all", False):
        return PUBLIC_METRICS | RESTRICTED_METRICS

    return set(
        permissions.get(
            "allowed_metrics",
            set(),
        )
    )