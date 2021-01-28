from flask import Flask, request
from modules.log.log import logger
from alice_skill.request import Request
from alice_skill.scenes import DEFAULT_SCENE
application = Flask(__name__)


@application.route('/post', methods=['POST'])
def main():
    logger.info(request.json)
    event = request.json
    req = Request(event)
    current_scene_id = event.get('state', {}).get('session_state', {}).get('scene')
    if current_scene_id is None:
        return DEFAULT_SCENE().reply(req)


if __name__ == "__main__":
    application.run(host="0.0.0.0", port="1337")
