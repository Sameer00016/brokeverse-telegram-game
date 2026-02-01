LUXURY_ITEMS = {
    "suit": {"level": 9, "cost": 0.1},
    "car": {"level": 9, "cost": 0.2},
    "villa": {"level": 10, "cost": 0.3},
    "yacht": {"level": 10, "cost": 0.5},
}

def can_unlock(user_level, item):
    return user_level >= LUXURY_ITEMS[item]["level"]
