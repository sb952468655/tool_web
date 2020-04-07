from flask import Blueprint

special_line = Blueprint('special_line', __name__)

from . import views