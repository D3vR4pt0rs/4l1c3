import os
from modules.alice_library.alice import YandexAlice

# Library
ALICE = YandexAlice(os.environ.get('OAUTH_TOKEN'), os.environ.get("SKILL_ID"))
SESSION_STORAGE = {}

# State
STATE_REQUEST_KEY = 'session'
STATE_RESPONSE_KEY = 'session_state'

#Scene
QUIZ = 'Quiz'
QUEST = 'Quest'

# Intents
START_TOUR = 'start_tour'
START_TOUR_WITH_PLACE = 'start_tour_with_place'
START_ACTIVITY = 'start_activity'
START_ACTIVITY_SHORT = 'start_activity_short'
FIND_NEAR_PLACE = 'find_near_place'
STOP_ACTIVITY = 'stop_activity'

# Coordinates
ENCHANTRESS_location = {'lat': 58.521698, 'lon': 31.268701}
ZAVOD_BAR_location = {'lat': 58.52703,'lon': 31.259656}
JAZZ_BLUES_location = {'lat': 58.518129,'lon': 31.286911}
GOAT_location = {'lat': 58.526687,'lon': 31.279455}