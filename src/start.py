from flask import Flask, request
import json
import os
from modules.alice_library.alice import YandexAlice

application = Flask(__name__)
alice = YandexAlice(os.environ.get('OAUTH_TOKEN'), os.environ.get("SKILL_ID"))


@application.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)
    return json.dumps(response)


def handle_dialog(res, req):
    if req['request']['original_utterance']:
        if req['request']['payload']['action'] == 'start':
            res['response'][
                'text'] = "Добрый день путник, я Захар, ваш личный помощник, сомилье и гид в мире алкоголя Великого Новгорода."
    else:
        res['response'][
            'text'] = "Добро пожаловать в навык Bar'ские приключения. В ходе прохождения нашего навыка вы узнаете мног интересного об истории некоторых пивоварен и мест связанных с данной тематикой."
        res['response']['buttons'] = alice.create_button(title="Начать приключение", payload={"action": "start"})


if __name__ == "__main__":
    application.run(host="0.0.0.0", port="1337")
