from flask import Flask, request
from modules.log.log import logger
from alice_skill.request import Request
from alice_skill.constants import STATE_REQUEST_KEY, QUEST, QUIZ
from alice_skill.scenes import DEFAULT_SCENE, SCENES, Quiz, Quest
application = Flask(__name__)


@application.route('/post', methods=['POST'])
def main():
    logger.info(request.json)
    event = request.json
    req = Request(event)
    current_scene_id = event.get('state').get(STATE_REQUEST_KEY).get('scene')

    if current_scene_id is None:
        return DEFAULT_SCENE().reply(req)
    elif current_scene_id == QUIZ:
        return Quiz().reply(req)
    elif current_scene_id == QUEST:
        return Quest().reply(req)

    current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
    next_scene = current_scene.move(req)
    if next_scene is not None:
        logger.info(f'Moving from scene {current_scene.id()} to {next_scene.id()}')
        return next_scene.reply(req)
    else:
        logger.info(f'Failed to parse user request at scene {current_scene.id()}')
        return current_scene.fallback()


if __name__ == "__main__":
    application.run(host="0.0.0.0", port="6666")
