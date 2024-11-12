import time
class Cooldown:
    def __init__(self, countdown: float):
        self.record = {}
        self.countdown = countdown
    def use(self, group_id: int) -> bool:
        if group_id not in self.record: self.record[group_id] = 0.0
        if time.time() - self.record[group_id] >= self.countdown:
            self.record[group_id] = time.time()
            return True
        return False