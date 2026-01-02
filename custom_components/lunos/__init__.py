"""LUNOS Ventilation Fan Control for Home Assistant.

This integration currently uses legacy YAML configuration and forwards setup to
the fan platform.

https://github.com/rsnodgrass/hass-lunos
"""

import logging
from pathlib import Path
from typing import Any

import yaml

try:
    # Newer Home Assistant versions
    from homeassistant.helpers.discovery import async_load_platform
except ImportError:  # pragma: no cover
    async_load_platform = None
    from homeassistant.helpers.discovery import load_platform

from .const import LUNOS_DOMAIN

LOG = logging.getLogger(__name__)

LUNOS_CODING_CONFIG: dict[str, Any] = {}
_CODINGS_FILE = Path(__file__).with_name('lunos-codings.yaml')


def _load_coding_config() -> None:
    """Load lunos-codings.yaml into the module-level LUNOS_CODING_CONFIG."""
    global LUNOS_CODING_CONFIG
    try:
        with _CODINGS_FILE.open(encoding='utf-8') as file:
            data = yaml.safe_load(file) or {}
        if not isinstance(data, dict):
            raise ValueError('Expected lunos-codings.yaml to contain a mapping at the top level')
        LUNOS_CODING_CONFIG = data
    except Exception:
        LOG.exception("Failed to load LUNOS config '%s'", _CODINGS_FILE)
        LUNOS_CODING_CONFIG = {}


async def async_setup(hass, config):
    # Load static model/coding metadata before platform import so the fan platform
    # schema (vol.In(LUNOS_CODING_CONFIG.keys())) has the expected keys.
    if not LUNOS_CODING_CONFIG:
        _load_coding_config()

    LOG.info("LUNOS controller codings supported: %s", list(LUNOS_CODING_CONFIG.keys()))

    conf = config.get(LUNOS_DOMAIN)
    if conf is None:
        LOG.info("No LUNOS configuration found")
        return True

    if async_load_platform is not None:
        await async_load_platform(hass, "fan", LUNOS_DOMAIN, None, conf)
    else:  # pragma: no cover
        load_platform(hass, "fan", LUNOS_DOMAIN, None, conf)

    return True
