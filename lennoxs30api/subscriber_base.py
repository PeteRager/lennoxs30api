# pylint: disable=line-too-long
"""Base class for subscribable objects"""
from abc import ABC, abstractmethod
import logging

_LOGGER = logging.getLogger(__name__)


class SubscriberBase(ABC):
    """Base class for subscribable objects"""

    def __init__(self):
        self._dirty_list: list[str] = []
        self._callbacks = []
        self._dirty = False

    @abstractmethod
    def debug_string(self) -> str:
        """Returns string to be logged in messages"""

    def attr_updater(self, data_set, attr: str, property_name: str = None) -> bool:
        """Updates an attribue"""
        if attr in data_set:
            attr_val = data_set[attr]
            if property_name is None:
                property_name = attr
            if getattr(self, property_name) != attr_val:
                setattr(self, property_name, attr_val)
                self._dirty = True
                if property_name not in self._dirty_list:
                    self._dirty_list.append(property_name)
                    _LOGGER.debug(
                        "update_attr: [%s] attr [%s] value [%s]", self.debug_string(), property_name, attr_val
                    )
                return True
        return False

    def register_on_update_callback(self, callbackfunc, match=None):
        """Register a callback for changes"""
        self._callbacks.append({"func": callbackfunc, "match": match})

    def execute_on_update_callbacks(self):
        """Execute callbacks"""
        if self._dirty:
            for callback in self._callbacks:
                callbackfunc = callback["func"]
                match = callback["match"]
                matches = False
                if match is None:
                    matches = True
                else:
                    for match_item in match:
                        if match_item in self._dirty_list:
                            matches = True
                            break
                try:
                    if matches:
                        callbackfunc()
                except Exception:  # pylint: disable=broad-exception-caught
                    # Log and eat this exception so we can process other callbacks
                    _LOGGER.exception("executeOnUpdateCallback - [%s] - failed", self.debug_string())
        self._dirty = False
        self._dirty_list = []
