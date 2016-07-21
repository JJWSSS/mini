from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentucated, comment, good, order, user
