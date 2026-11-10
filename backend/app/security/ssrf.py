"""SSRF protection for website URL ingestion.

Blocks localhost, private IP ranges (RFC 1918), link-local addresses, and
cloud metadata endpoints. Validates URL schemes and redirect targets.
"""

import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple

# Private/reserved IP ranges that must never be accessed.
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # localhost
    ipaddress.ip_network("10.0.0.0/8"),        # RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),     # RFC 1918
    ipaddress.ip_network("192.168.0.0/16"),    # RFC 1918
    ipaddress.ip_network("169.254.0.0/16"),    # link-local / cloud metadata
    ipaddress.ip_network("::1/128"),           # IPv6 localhost
    ipaddress.ip_network("fc00::/7"),          # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),         # IPv6 link-local
    ipaddress.ip_network("100.64.0.0/10"),     # carrier-grade NAT
    ipaddress.ip_network("192.0.2.0/24"),      # TEST-NET
    ipaddress.ip_network("198.51.100.0/24"),   # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),    # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),       # multicast
    ipaddress.ip_network("240.0.0.0/4"),       # reserved
]

ALLOWED_SCHEMES = {"http", "https"}

# Cloud metadata endpoints (by hostname) - extra belt-and-suspenders beyond IP checks.
BLOCKED_HOSTNAMES = {
    "169.254.169.254",       # AWS / Azure / GCP metadata
    "metadata.google.internal",
    "metadata.azure.com",
    "169.254.169.254",
}


def _is_blocked_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # cannot parse => treat as blocked
    return any(ip in net for net in BLOCKED_NETWORKS)


def resolve_hostname(hostname: str) -> Tuple[bool, str | None]:
    """Resolve a hostname and return (is_allowed, reason). Resolves to IPs and
    blocks any address that falls in a private/reserved range."""
    try:
        infos = socket.getaddrinfo(hostname, None, family=socket.AF_UNSPEC)
    except socket.gaierror:
        return False, "Unable to resolve hostname"

    for family, _type, _proto, _canon, sockaddr in infos:
        ip_str = sockaddr[0]
        if _is_blocked_ip(ip_str):
            return False, f"Resolved to blocked address {ip_str}"
    return True, None


def validate_url(url: str) -> Tuple[bool, str | None, str | None]:
    """Validate a user-supplied URL for SSRF safety.

    Returns (is_valid, normalized_url, error_reason).
    """
    if not url or not url.strip():
        return False, None, "URL is required"

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception:
        return False, None, "Invalid URL"

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False, None, f"Scheme '{parsed.scheme}' not allowed. Use http or https."

    if not parsed.hostname:
        return False, None, "URL must include a hostname"

    hostname = parsed.hostname.lower()
    if hostname in BLOCKED_HOSTNAMES:
        return False, None, f"Hostname '{hostname}' is blocked"

    # If hostname is a literal IP, check it directly.
    allowed, reason = resolve_hostname(hostname)
    if not allowed:
        return False, None, reason

    return True, url, None


def is_redirect_safe(next_url: str) -> Tuple[bool, str | None]:
    """Check a redirect target URL for SSRF safety."""
    return validate_url(next_url)
