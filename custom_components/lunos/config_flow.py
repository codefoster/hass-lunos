"""Config flow for the LUNOS ventilation integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from . import async_get_coding_keys
from .const import (
    CONF_CONTROLLER_CODING,
    CONF_DEFAULT_SPEED,
    CONF_FAN_COUNT,
    CONF_RELAY_W1,
    CONF_RELAY_W2,
    DEFAULT_LUNOS_NAME,
    DEFAULT_SPEED,
    LUNOS_DOMAIN,
    SPEED_LIST,
)


def _coding_options(hass: HomeAssistant) -> list[str]:
    # Ensure codings are loaded for selectors and validation.
    return list(async_get_coding_keys(hass))


def _config_schema(hass: HomeAssistant, *, defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}

    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_LUNOS_NAME)): TextSelector(
                TextSelectorConfig()
            ),
            vol.Required(CONF_RELAY_W1, default=defaults.get(CONF_RELAY_W1, "")): EntitySelector(
                EntitySelectorConfig(domain=["switch"])
            ),
            vol.Required(CONF_RELAY_W2, default=defaults.get(CONF_RELAY_W2, "")): EntitySelector(
                EntitySelectorConfig(domain=["switch"])
            ),
            vol.Optional(
                CONF_CONTROLLER_CODING,
                default=defaults.get(CONF_CONTROLLER_CODING, "e2-usa"),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=_coding_options(hass),
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_DEFAULT_SPEED,
                default=defaults.get(CONF_DEFAULT_SPEED, DEFAULT_SPEED),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=SPEED_LIST,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_FAN_COUNT,
                default=defaults.get(CONF_FAN_COUNT, 2),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=1,
                    max=4,
                    step=1,
                    mode=NumberSelectorMode.BOX,
                )
            ),
        }
    )


def _unique_id_from_relays(relay_w1: str, relay_w2: str) -> str:
    # Keep it stable and human-debuggable; entity_ids are already normalized.
    return f"{relay_w1}|{relay_w2}"


class LunosConfigFlow(config_entries.ConfigFlow, domain=LUNOS_DOMAIN):
    """Handle a config flow for LUNOS."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            relay_w1 = cv.entity_id(user_input[CONF_RELAY_W1])
            relay_w2 = cv.entity_id(user_input[CONF_RELAY_W2])

            await self.async_set_unique_id(_unique_id_from_relays(relay_w1, relay_w2))
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=user_input.get(CONF_NAME, DEFAULT_LUNOS_NAME), data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_config_schema(self.hass),
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        """Import configuration from YAML."""
        # Called from async_setup when a legacy YAML config is detected.
        relay_w1 = cv.entity_id(user_input[CONF_RELAY_W1])
        relay_w2 = cv.entity_id(user_input[CONF_RELAY_W2])

        await self.async_set_unique_id(_unique_id_from_relays(relay_w1, relay_w2))
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=user_input.get(CONF_NAME, DEFAULT_LUNOS_NAME), data=user_input)
