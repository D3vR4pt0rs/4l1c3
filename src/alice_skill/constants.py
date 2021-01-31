import os
from modules.alice_library.alice import YandexAlice

# Library
ALICE = YandexAlice(os.environ.get('OAUTH_TOKEN'), os.environ.get("SKILL_ID"))

# State
STATE_REQUEST_KEY = 'session'
STATE_RESPONSE_KEY = 'session_state'

# Intents
START_TOUR = 'start_tour'
START_TOUR_WITH_PLACE = 'start_tour_with_place'
START_ACTIVITY = 'start_activity'
START_ACTIVITY_SHORT = 'start_activity_short'