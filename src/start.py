from flask import Flask, request
import json

application = Flask(__name__)


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
        res['response']['text'] = req['request']['original_utterance']
        res['response']['buttons'] = [
            {
             "title":"test",
             "payload":{},
             "url": "https://google.com/",
             "hide": "false"
            }
        ]
    else:
        res['response']['text'] = ""


if __name__ == "__main__":
    application.run(host="0.0.0.0", port="1337")
