from abc import ABC, abstractmethod
from modules.alice_library.alice import GEOLOCATION_ALLOWED, GEOLOCATION_REJECTED
from modules.log.log import logger
from alice_skill.intents import START_TOUR
from alice_skill.constants import ALICE
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
    def handle_local_intents(request: Request):
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
            'session_state': {
                'scene': self.id(),
            },
        }
        if state is not None:
            webhook_response['session_state'].update(state)
        return webhook_response


class BarTourScene(Scene):
    def handle_global_intents(self, request):
        if START_TOUR in request.intents:
            return StartTour()


class Welcome(BarTourScene):
    def reply(self, request: Request):
        text = ("Добро пожаловать в навык Bar'ские приключения."
                'В ходе прохождения нашего навыка вы узнаете мног интересного об истории некоторых пивоварен и мест связанных с данной тематикой.'
                'Но прежде дайте дайте доступ к геолокации чтобы я понимал, где вы находитесь.')
        directives = {'request_geolocation': {}}
        return self.make_response(text, buttons=[
            ALICE.create_button('Начать приключение', hide=True),
        ], directives=directives)

    def handle_local_intents(self, request: Request):
        logger.info('request type: ' + request.type)
        if request.type in (
                GEOLOCATION_ALLOWED,
                GEOLOCATION_REJECTED,
        ):
            return HandleGeolocation()


class StartTour(BarTourScene):
    def reply(self, request: Request):
        text = 'Вы в Великом Новгороде, на территории старинного кремля. Возле какого места вы находитесь?'
        return self.make_response(text, state={
            'screen': 'start_tour'
        }, buttons=[
            ALICE.create_button('Спасская башня'),
            ALICE.create_button('Софийский собор'),
        ])


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

DEFAULT_SCENE = Welcome