# api id, hash
API_ID = 14895435
API_HASH = "e8205235cc85f4d3b9b8733a24954950"

DELAYS = {
    "ACCOUNT": [
        5,
        15,
    ],  # delay between connections to accounts (the more accounts, the longer the delay)
    "PLAY": [5, 15],  # delay between play in seconds
    "ERROR_PLAY": [60, 180],  # delay between errors in the game in seconds
}

# points with each play game; max 280
POINTS = [240, 280]

# title blacklist tasks (do not change)
BLACKLIST_TASKS = ["Farm points"]

# session folder (do not change)
WORKDIR = "sessions/"

ACCOUNT_PER_ONCE = 3
PROXY = False
