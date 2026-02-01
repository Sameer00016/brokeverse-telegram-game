import time

user_taps = {}

def check_tap(user_id):
    now = time.time()
    if user_id in user_taps and now - user_taps[user_id] < 0.2:
        return False
    user_taps[user_id] = now
    return True
