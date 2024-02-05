"""Modules for lennox schedules"""
# pylint: disable=invalid-name

from .lennox_period import lennox_period

class lennox_schedule(object):
    """Class for a lennox schedule"""
    def __init__(self, sched_id):
        self.id = sched_id
        self.name = '<Unknown>'
        self.periodCount = -1
        self._periods = []

    def getOrCreatePeriod(self, period_id: int) -> lennox_period:
        """Returns an existing or creates a new period"""
        item = self.getPeriod(period_id)
        if item is not None:
            return item
        item = lennox_period(period_id)
        self._periods.append(item)
        return item

    def getPeriod(self, period_id: int) -> lennox_period:
        """Returns a period by id"""
        for item in self._periods:
            if item.id == period_id:
                return item
        return None

    def update(self, tschedule: dict) -> None:
        """Updates the schedule from a JSON dict"""
        if 'schedule' not in tschedule:
            return
        schedule = tschedule['schedule']
        if 'name' in schedule:
            self.name = schedule['name']
        if 'periodCount' in schedule:
            self.periodCount = schedule['periodCount']
        if 'periods' in schedule:
            for periods in schedule['periods']:
                periodId = periods['id']
                lperiod = self.getOrCreatePeriod(periodId)
                lperiod.update(periods)
                