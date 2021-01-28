import os
from modules.alice_library.alice import YandexAlice

ALICE = YandexAlice(os.environ.get('OAUTH_TOKEN'), os.environ.get("SKILL_ID"))