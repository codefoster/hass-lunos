"""LUNOS Ventilation Fan Control for Home Assistant.

This custom integration supports config entries (UI config flow) and can import
legacy YAML configuration.

https://github.com/rsnodgrass/hass-lunos
"""

import logging
from pathlib import Path
from typing import Any

import yaml

from homeassistant import config_entries
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import LUNOS_DOMAIN

LOG = logging.getLogger(__name__)

LUNOS_CODING_CONFIG: dict[str, Any] = {}
_CODINGS_FILE = Path(__file__).with_name('lunos-codings.yaml')

PLATFORMS: list[Platform] = [Platform.FAN]


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


def async_get_coding_keys(hass: HomeAssistant) -> list[str]:
    """Return the available controller coding keys.

    The list is backed by `lunos-codings.yaml` which ships with the integration.
    """

    if not LUNOS_CODING_CONFIG:
        _load_coding_config()
    return list(LUNOS_CODING_CONFIG.keys())


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up LUNOS.

    If legacy YAML is present, start an import flow to migrate it into a config
    entry.
    """

    if not LUNOS_CODING_CONFIG:
        _load_coding_config()

    if conf := config.get(LUNOS_DOMAIN):
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                LUNOS_DOMAIN,
                context={"source": config_entries.SOURCE_IMPORT},
                data=conf,
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Set up LUNOS from a config entry."""

    if not LUNOS_CODING_CONFIG:
        _load_coding_config()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
