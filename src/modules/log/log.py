import logging
from werkzeug.serving import WSGIRequestHandler, _log


log_level = "INFO"
log_format = '[%(asctime)s] [%(levelname)s] "%(message)s"'
date_format = "%d/%b/%Y:%H:%M:%S %z"

handler = logging.StreamHandler()
formatter = logging.Formatter(log_format, date_format)
handler.setFormatter(formatter)
# Adding to root in order to affect wsgi logs as well
root = logging.getLogger()
root.addHandler(handler)

logger = logging.getLogger("app")
logger.setLevel(log_level)


class MyRequestHandler(WSGIRequestHandler):
    def log(self, type, message, *args):
        _log(type, f"{self.address_string()} {message % args}\n")

    def log_request(self, code="-"):
        self.log("info", f"{self.requestline} {code}")