import falcon

from .tokens import AuthHandlerSession
from .tokens import PubKeyHandler
from .config_data import applications
from .sessions import SessionException



def main():
   api = falcon.App()
   for app in applications:
      api.add_route('/session/' + app, AuthHandlerSession(app))
      api.add_route('/pubkeys/' + app, PubKeyHandler(app))
      api.add_error_handler(SessionException)
   return api
