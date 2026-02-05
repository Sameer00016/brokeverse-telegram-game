# Points required per level
LEVELS = {
    1: 0,
    2: 1_000,
    3: 5_000,
    4: 20_000,
    5: 100_000,
    6: 500_000,
    7: 1_000_000,
    8: 5_000_000,
    9: 10_000_000,
    10: 20_000_000
}

# Tap upgrade rewards (level → points per tap)
TAP_UPGRADES = {i: i for i in range(1, 51)}

# Daily claim rewards
CLAIM_UPGRADES = {
    i: i * 1000 for i in range(1, 51)
}
