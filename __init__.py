import asyncio

"""Support for Arduino boards running with the Firmata firmware."""
import logging

from pymata_express.pymata_express import PymataExpress
import serial
import voluptuous as vol

from homeassistant.const import (
    CONF_PORT,
    EVENT_HOMEASSISTANT_START,
    EVENT_HOMEASSISTANT_STOP,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "arduino"
CONF_BAUD = "baud_rate"

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema(
        {
            vol.Required(CONF_PORT): cv.string,
            vol.Optional(CONF_BAUD, default=57600): cv.positive_int
        }
    )}, extra=vol.ALLOW_EXTRA
)


def setup(hass, config):
    """Set up the Arduino component."""

    port = config[DOMAIN][CONF_PORT]
    baud_rate = config[DOMAIN][CONF_BAUD]

    asyncio.set_event_loop(asyncio.new_event_loop())
    try:
        board = PymataExpress(port, baud_rate)
    except (serial.serialutil.SerialException, FileNotFoundError):
        _LOGGER.error("Your port %s is not accessible", port)
        return False

    async def stop_arduino(event):
        """Stop the Arduino service."""
        await board.shutdown()

    async def start_arduino(event):
        """Start the Arduino service."""
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop_arduino)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, start_arduino)
    hass.data[DOMAIN] = board

    return True
