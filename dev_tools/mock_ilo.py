#!/usr/bin/env python
from flask import Flask, request

import json
import logging
import os

logging.basicConfig(
    format="%(levelname)s %(asctime)s [%(name)s] - %(message)s", level=os.environ.get("LOGLEVEL", "INFO")
)

app = Flask(__name__)


def load(src):
    with open(src) as json_file:
        return json.load(json_file)


def debug(logger, request):
    logger.info("{}: uri: {}".format(request.method, request.url))
    logger.info("{}: header: {}".format(request.method, request.headers))
    if request.method in ["PATCH", "PUT" "POST"]:
        logger.info("{}: payload: {}".format(request.method, request.get_json(force=True)))


@app.route("/redfish/v1/Managers/1/SecurityService", methods=["GET", "PATCH"])
def security_service():
    logger = logging.getLogger("security_service")
    debug(logger, request)
    if request.method == "PATCH":
        return "", 204
    elif request.method == "GET":
        return load("ilo_responses/SecurityService.json")


@app.route("/redfish/v1/Chassis/1/Thermal", methods=["GET", "PATCH"])
def thermal():
    logger = logging.getLogger("thermal")
    debug(logger, request)
    if request.method == "PATCH":
        return "", 204
    elif request.method == "GET":
        return load("ilo_responses/thermal.json")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
