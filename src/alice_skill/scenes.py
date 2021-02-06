import enum
import inspect
import sys
import math
from abc import ABC, abstractmethod
from typing import Optional

from constants import (
    ENCHANTRESS_location,
    ZAVOD_BAR_location,
    JAZZ_BLUES_location,
    GOAT_location
)

from modules.alice_library.alice import (
    GEOLOCATION_ALLOWED,
    GEOLOCATION_REJECTED,
)
from modules.log.log import logger

import alice_skill.constants as alice
from alice_skill.helper import check_time
from alice_skill.request import Request


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

    def fallback(self):
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
        elif alice.FIND_NEAR_PLACE in request.intents:
            return move_to_place_scene(request)


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
        logger.info('request type: ' + request.type)
        if request.type in (
                GEOLOCATION_ALLOWED,
                GEOLOCATION_REJECTED,
        ):
            return HandleGeolocation()


class StartQuest(BarTourScene):
    def reply(self, request: Request):
        text = f'{check_time()}, путник. Не хочешь ли поучаствовать в квесте и узнать историю алкоголя в Великом Новгороде?'
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
            text = ('К сожалению, мне не удалось получить ваши координаты.' 
                    'Поэтому я не могу вам советовать и провести квест, но можем поиграть в викторину')
            return self.make_response(text, directives={'request_geolocation': {}})

    def handle_local_intents(self, request: Request):
        pass


class Activity(enum.Enum):
    UNKNOWN = 1
    NOT_ALLOWED = 2
    QUEST = 3
    QUIZ = 4
    ADVICE = 5

    @classmethod
    def from_request(cls, request: Request, intent_name: str):
        slot = request.intents[intent_name]['slots']['place']['value']
        if slot == 'quest':
            if request.type == GEOLOCATION_ALLOWED:
                return cls.QUEST
            else:
                return cls.NOT_ALLOWED
        if slot == 'advice':
            if request.type == GEOLOCATION_ALLOWED:
                return cls.ADVICE
            else:
                return cls.NOT_ALLOWED
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
    elif activity == Activity.ADVICE:
        return Advice()
    elif activity == Activity.UNKNOWN:
        return Unknown()
    elif activity == Activity.NOT_ALLOWED:
        return NotAllowed()


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


class Advice(BarTourScene):
    def reply(self, request: Request):
        return self.make_response(text='Советы давать не могу и тебе не советую')

    def handle_local_intents(self, request: Request):
        pass


class Unknown(BarTourScene):
    def reply(self, request: Request):
        return self.make_response(text='Извини друг, я понимаю что ты хочешь.')

    def handle_local_intents(self, request: Request):
        pass


class NotAllowed(BarTourScene):
    def reply(self, request: Request):
        return self.make_response(text='Прости, но пока Большой брат не следит за тобой, я не могу помочь.')

    def handle_local_intents(self, request: Request):
        pass





class Place(enum.Enum):
    ENCHANTRESS = 1
    ZAVOD_BAR = 2
    JAZZ_BLUES = 3
    GOAT = 4

    def _distance(cls, client_location={}, bar_location={}):
        return math.sqrt(pow((bar_location['lat'] - client_location['lat']), 2) + pow((bar_location['lon'] - client_location['lon']), 2))

    @classmethod
    def place_from_geolocation(cls, request: Request):
        location_full = request['session']['location']
        location = {location_full['lat'], location_full['lon']}
        #location = {'lat': 58.521698, 'lon': 31.268701}

        distances = {}
        distances.update(enchantress=cls._distance(location, ENCHANTRESS_location))
        distances.update(zavod_bar=cls._distance(location, ZAVOD_BAR_location))
        distances.update(jazz_blues=cls._distance(location, JAZZ_BLUES_location))
        distances.update(goat=cls._distance(location, GOAT_location))
        min_distanation = min(distances.values())

        #logger
        logger.info(distances)

        if distances['enchantress'] == min_distanation: return cls.ENCHANTRESS
        if distances['zavod_bar'] == min_distanation: return cls.ZAVOD_BAR
        if distances['jazz_blues'] == min_distanation: return cls.JAZZ_BLUES
        if distances['goat'] == min_distanation: return cls.GOAT


def move_to_place_scene(request: Request):
    place = Place.place_from_geolocation(request)
    if place == Place.ZAVOD_BAR:
        return Zavod()
    elif place == Place.GOAT:
        return None
    elif place == Place.ENCHANTRESS:
        return None
    elif place == Place.JAZZ_BLUES:
        return None


class Zavod(BarTourScene):
    def reply(self, request: Request):
        tts = ('Завод бар. Данный бар располагается в бывшей проходной завода Алкон.'
               'В данном заведении русская кухня. Если хотите узнать больше о Алконе, пройдите наш квест. '
               )
        return self.make_response(
            text='',
            tts=tts,
            card=alice.create_image_gallery(image_ids=[
                '213044/6b28d20a9faa88496151'
            ])
        )

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
