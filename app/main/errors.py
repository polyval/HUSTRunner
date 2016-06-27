from flask import render_template, current_app

from . import main


@main.app_errorhandler(404)
def internal_server_error(exception):
    app = current_app._get_current_object()
    app.logger.error(exception)
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(exception):
    app = current_app._get_current_object()
    app.logger.error(exception)
    return render_template('500.html'), 500
