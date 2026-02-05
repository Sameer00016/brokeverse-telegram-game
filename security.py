import time
from config import MAX_TAPS_PER_SECOND, DAILY_CLAIM_COOLDOWN

_last_tap = {}

def anti_tap(user):
    uid = id(user)
    now = time.time()
    if uid in _last_tap:
        if now - _last_tap[uid] < (1 / MAX_TAPS_PER_SECOND):
            user["warnings"] += 1
            if user["warnings"] > 10:
                user["banned"] = True
            return False
    _last_tap[uid] = now
    return True


def can_claim(user):
    return time.time() - user["last_claim"] >= DAILY_CLAIM_COOLDOWN
