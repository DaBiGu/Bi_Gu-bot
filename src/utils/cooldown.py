import time
from typing import Tuple
class Cooldown:
    def __init__(self, countdown: float):
        self.record = {}
        self.countdown = countdown
    def use(self, group_id: int) -> Tuple[bool, int]:
        if group_id not in self.record: self.record[group_id] = 0.0
        time_elapsed = time.time() - self.record[group_id]
        if time_elapsed >= self.countdown:
            self.record[group_id] = time.time()
            return (True, 0)
        return (False, int(self.countdown - time_elapsed))