from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from app.user.models import Permission


@main.app_context_processor
def inject_permissions():
    """
    A context processor is a function that returns
    a dictionary, it can inject new values into the
    template context.
    """
    return dict(Permission=Permission)