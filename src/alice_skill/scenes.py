import enum
import inspect
import sys
from abc import ABC, abstractmethod
from typing import Optional
from modules.alice_library.alice import (
    GEOLOCATION_ALLOWED,
    GEOLOCATION_REJECTED,
)

from alice_skill.request import Request
import alice_skill.constants as alice


class Place(enum.Enum):
    UNKNOWN = 1
    TOWER = 2
    CATHEDRAL = 3

    @classmethod
    def from_request(cls, request: Request, intent_name: str):
        slot = request.intents[intent_name]['slots']['place']['value']
        if slot == 'tower':
            return cls.TOWER
        elif slot == 'cathedral':
            return cls.CATHEDRAL
        else:
            return cls.UNKNOWN


def move_to_place_scene(request: Request, intent_name: str):
    place = Place.from_request(request, intent_name)
    if place == Place.TOWER:
        return Tower()
    elif place == Place.CATHEDRAL:
        return Cathedral()


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
            return StartTour()
        elif alice.START_TOUR_WITH_PLACE in request.intents:
            return move_to_place_scene(request, alice.START_TOUR_WITH_PLACE)


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


class StartTour(BarTourScene):
    def reply(self, request: Request):
        text = ''
        return self.make_response(text, state={
            'screen': 'start_tour'
        }, buttons=[
            alice.ALICE.create_button('Спасская башня'),
            alice.ALICE.create_button('Софийский собор'),
        ])

    def handle_local_intents(self, request: Request):
        if alice.START_TOUR_WITH_PLACE_SHORT:
            return move_to_place_scene(request, alice.START_TOUR_WITH_PLACE_SHORT)


class Tower(BarTourScene):
    def reply(self, request: Request):
        tts = ('Спасская башня. Спасская башня — проездная башня Новгородского детинца, строение конца XV века. '
            'Башня шестиярусная, в плане представляет собой вытянутый прямоугольник 15 × 8,3 м.'
            'Ширина проезда — 3 м. Высота стен — 19 м, а толщина стен на уровне второго яруса — 2 м.'
        )
        return self.make_response(
            text='',
            tts=tts,
            card=alice.ALICE.create_image_gallery(image_ids=[
                '213044/6d63099949494a74d4a0',
                '997614/89f90bf8bca41f92c85c',
            ])
        )

    def handle_local_intents(self, request: Request):
        pass


class Cathedral(BarTourScene):
    def reply(self, request: Request):
        return self.make_response(text='В будущем здесь появится рассказ о Софийском соборе')

    def handle_local_intents(self, request: Request):
        pass


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