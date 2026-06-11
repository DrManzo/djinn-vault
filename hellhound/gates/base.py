"""base.py — Abstract Gate

All gate implementations inherit from BaseGate and implement:
    connect()     — establish connection to external service
    observe()     — generator/async-iterator yielding raw events
    disconnect()  — clean teardown
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator


class BaseGate(ABC):
    """
    Abstract base for all Hellhound gate adapters.

    A gate represents a single external data source (Discord, Telegram,
    Moonraker, network probes, etc.).  It is imported by pup-<name>.py
    and drives the observe() loop.
    """

    def __init__(self, name: str, config: dict | None = None):
        self.name   = name
        self.config = config or {}

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the external service."""

    @abstractmethod
    async def stream(self) -> AsyncIterator[dict]:
        """
        Async-iterate over raw events from the service.
        Each yielded dict should contain at minimum:
            {
                'domain':   str,   # e.g. 'comms', 'printer', 'network'
                'event':    str,   # e.g. 'msg_received', 'print_done'
                'payload':  dict,  # service-specific data
                'severity': str,   # 'debug'|'info'|'warning'|'error'
            }
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """Tear down the connection cleanly."""

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self.disconnect()
