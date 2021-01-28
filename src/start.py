from flask import Flask, request
from modules.log.log import logger
from alice_skill.request import Request
from alice_skill.scenes import DEFAULT_SCENE, SCENES
application = Flask(__name__)


@application.route('/post', methods=['POST'])
def main():
    logger.info(request.json)
    event = request.json
    req = Request(event)
    current_scene_id = event.get('state', {}).get('session_state', {}).get('scene')
    if current_scene_id is None:
        return DEFAULT_SCENE().reply(req)
    current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
    next_scene = current_scene.move(request)
    if next_scene is not None:
        print(f'Moving from scene {current_scene.id()} to {next_scene.id()}')
        return next_scene.reply(request)
    else:
        print(f'Failed to parse user request at scene {current_scene.id()}')
        return current_scene.fallback(request)


if __name__ == "__main__":
    application.run(host="0.0.0.0", port="1337")
