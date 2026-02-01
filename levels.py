LEVELS = {
    1: 0,
    2: 50000,
    3: 200000,
    4: 500000,
    5: 1000000,
    6: 2500000,
    7: 5000000,
    8: 8000000,
    9: 10000000,   # Luxury unlocks start here
    10: 20000000
}

# Tap upgrade multiplier
TAP_UPGRADES = {i: i*1 for i in range(1, 51)}  # Level 1 → 1 tap, Level 50 → 50 taps

# Daily claim upgrade multiplier
CLAIM_UPGRADES = {i: i*1000 for i in range(1, 51)}  # Level 1 → 1000 pts, Level 50 → 50k pts
