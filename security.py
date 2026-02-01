import time

def anti_tap(user):
    now = time.time()

    if "last_tap" not in user:
        user["last_tap"] = now
        user["tap_count"] = 1
        return True

    if now - user["last_tap"] < 1:
        user["tap_count"] += 1
    else:
        user["tap_count"] = 1
        user["last_tap"] = now

    if user["tap_count"] > 5:
        user["warnings"] += 1
        return False

    return True

def can_claim(user):
    return time.time() - user.get("last_claim", 0) >= 86400
