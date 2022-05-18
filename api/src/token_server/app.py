import falcon

from .tokens import AuthHandlerSession
from .tokens import PubKeyHandler
from .bad_request import BadRequest





def main():
   api = falcon.App()
   api.add_route('/session/reporting', AuthHandlerSession("reporting"))
   api.add_route('/pubkeys/reporting', PubKeyHandler("reporting"))
   api.add_error_handler(BadRequest) 
   return api
