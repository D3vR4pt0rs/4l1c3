import enum
import inspect
import sys
import datetime

from abc import ABC, abstractmethod
from typing import Optional
from modules.alice_library.alice import (
    GEOLOCATION_ALLOWED,
    GEOLOCATION_REJECTED,
)

from alice_skill.request import Request
import alice_skill.constants as alice


class Activity(enum.Enum):
    UNKNOWN = 1
    QUEST = 2
    QUIZ = 3

    @classmethod
    def from_request(cls, request: Request, intent_name: str):
        slot = request.intents[intent_name]['slots']['place']['value']
        if slot == 'quest':
            return cls.QUEST
        elif slot == 'quiz':
            return cls.QUIZ
        else:
            return cls.UNKNOWN


def move_to_activity_scene(request: Request, intent_name: str):
    activity = Activity.from_request(request, intent_name)
    if activity == Activity.QUIZ:
        return Quiz()
    elif activity == Activity.QUEST:
        return Quest()


def check_time():
    opts = {"hey": ('Доброе утро', 'Добрый день', 'Добрый вечер', 'Доброй ночи')}

    now = datetime.datetime.now()
    now += datetime.timedelta(hours=3)
    if 4 < now.hour <= 12:
        greet = opts["hey"][0]
    if 12 < now.hour <= 16:
        greet = opts["hey"][1]
    if 16 < now.hour <= 24:
        greet = opts["hey"][2]
    if 0 <= now.hour <= 4:
        greet = opts["hey"][3]
    return greet


class Scene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    """Генерация ответа сцены"""

    @abstractmethod
    def reply(self, request):
        raise NotImplementedError()

    """Проверка перехода к новой сцене"""

    def move(self, request: Request):
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    @abstractmethod
    def handle_global_intents(self):
        raise NotImplementedError()

    @abstractmethod
    def handle_local_intents(request: Request) -> Optional[str]:
        raise NotImplementedError()

    def fallback(self, request: Request):
        return self.make_response('Извините, я вас не поняла. Пожалуйста, попробуйте переформулировать вопрос.')

    def make_response(self, text, tts=None, card=None, state=None, buttons=None, directives=None):
        response = {
            'text': text,
            'tts': tts if tts is not None else text,
        }
        if card is not None:
            response['card'] = card
        if buttons is not None:
            response['buttons'] = buttons
        if directives is not None:
            response['directives'] = directives
        webhook_response = {
            'response': response,
            'version': '1.0',
            alice.STATE_RESPONSE_KEY: {
                'scene': self.id(),
            },
        }
        if state is not None:
            webhook_response[alice.STATE_RESPONSE_KEY].update(state)
        return webhook_response


class BarTourScene(Scene):

    def handle_global_intents(self, request):
        if alice.START_TOUR in request.intents:
            return StartQuest()
        elif alice.START_ACTIVITY in request.intents:
            return move_to_activity_scene(request, alice.START_ACTIVITY)


class Welcome(BarTourScene):
    def reply(self, request: Request):
        text = ('Добро пожаловать в Барские приключения. '
                'Данный навык призван рассказать историю алкоголя Великого Новгорода и провести по наиболее значимым местам.'
                'Но прежде дайте доступ к геолокации, чтобы я понимал, где вы находитесь.')
        directives = {'request_geolocation': {}}
        return self.make_response(text, buttons=[
            alice.ALICE.create_button('Расскажи экскурсию', hide=True),
        ], directives=directives)

    def handle_local_intents(self, request: Request):
        print('request type: ' + request.type)
        if request.type in (
                GEOLOCATION_ALLOWED,
                GEOLOCATION_REJECTED,
        ):
            return HandleGeolocation()


class StartQuest(BarTourScene):
    def reply(self, request: Request):
        text = f'{check_time()},путник. Не хочешь ли поучаствовать в квесте и узнать историю алкоголя в Великом Новгороде?'
        return self.make_response(text, state={
            'screen': 'start_tour'
        }, buttons=[
            alice.ALICE.create_button('Спасская башня'),
            alice.ALICE.create_button('Софийский собор'),
        ])

    def handle_local_intents(self, request: Request):
        if alice.START_ACTIVITY:
            return move_to_activity_scene(request, alice.START_ACTIVITY)


class HandleGeolocation(BarTourScene):
    def reply(self, request: Request):
        if request.type == GEOLOCATION_ALLOWED:
            location = request['session']['location']
            lat = location['lat']
            lon = location['lon']
            text = f'Ваши координаты: широта {lat}, долгота {lon}'
            return self.make_response(text)
        else:
            text = 'К сожалению, мне не удалось получить ваши координаты. Чтобы продолжить работу с навыком'
            return self.make_response(text, directives={'request_geolocation': {}})

    def handle_local_intents(self, request: Request):
        pass


class Quest(BarTourScene):
    def reply(self, request: Request):
        return self.make_response(text='Квестовик пьян, заходи в следующий раз.')

    def handle_local_intents(self, request: Request):
        pass


class Quiz(BarTourScene):
    def reply(self, request: Request):
        return self.make_response(text='К сожалению викторину мы пропили, но скоро вернем.')

    def handle_local_intents(self, request: Request):
        pass


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


SCENES = {
    scene.id(): scene for scene in _list_scenes()
}

DEFAULT_SCENE = Welcome
