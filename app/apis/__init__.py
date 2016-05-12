from flask import Blueprint

api = Blueprint('apis', __name__)

from . import views