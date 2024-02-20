"""Modules for a lennox home"""
# pylint: disable=invalid-name
# pylint: disable=line-too-long

import logging
import json

_LOGGER = logging.getLogger(__name__)


class lennox_home(object):
    """Class to model a lennox home"""
    def __init__(self, home_id: int):
        self.id: int = home_id
        self.idx: int = None
        self.name: str = None
        self.json: json = None
        _LOGGER.info("Creating lennox_home homeId [%s]", self.id)

    def update(self, home_idx: int, home_name: str, json_data: json) -> None:
        """Updates the object"""
        self.idx = home_idx
        self.name = home_name
        self.json = json_data
        _LOGGER.info("Updating lennox_home homeIdx [%s} homeId [%s] homeName [%s]",self.idx,self.id,self.name)
