import os
import six
import bcrypt
import falcon
import requests
from datetime import datetime

from . import json
from . import models
from . import config
from . import util


our_dir = os.path.abspath(os.path.dirname(__file__))
static_dir  = os.path.abspath(os.path.join(our_dir, '..', 'static'))


UNAUTH_ENDPOINTS = set(['/login', '/logout'])
def auth(req, resp, params):
    if req.path in UNAUTH_ENDPOINTS:
        return

    # Check the auth token.
    token = req.get_header('X-Auth-Token')
    if token is None:
        raise falcon.HTTPUnauthorized('Auth token required',
                                      'Please provide an auth token as part of '
                                      'the request.')

    # Set some sort of user parameter here.


def check_media_type(req, resp, params):
    if not req.client_accepts_json:
        raise falcon.HTTPUnsupportedMediaType(
            'Media type not supported',
            'This API only supports the JSON media type.')


def set_headers(req, resp, params):
    # TODO: set headers for CORS?
    req.set_header('X-UA-Compatible', 'IE=Edge')
    pass


class BaseResource(object):
    def __init__(self, db):
        self.db = db


def constant_compare(x, y):
    if len(x) != len(y):
        return False

    acc = 0
    for i in range(len(x)):
        acc += ord(x[i]) ^ ord(y[i])

    return acc == 0


class AuthenticateRoute(BaseResource):
    def on_post(self, req, resp):
        params = json.loads(req.stream.read())

        user_given = params.get('user')
        if user_given is None:
            raise falcon.HTTPBadRequest('Missing input parameter',
                                        'The "user" parameter is required.')

        password = params.get('password')
        if password is None:
            raise falcon.HTTPBadRequest('Missing input parameter',
                                        'The "password" parameter is required.')
        if isinstance(password, six.text_type):
            password = password.encode('utf-8')

        try:
            user = models.User.get(models.User.email == user_given)
        except models.User.DoesNotExist:
            raise falcon.HTTPBadRequest('Bad username or password',
                                        'A bad username or password was given.')

        # Hash the password - need to use constant-time compare here.
        res = bcrypt.hashpw(password, user.password.encode('utf-8'))
        if not constant_compare(res, user.password):
            raise falcon.HTTPBadRequest('Bad username or password',
                                        'A bad username or password was given.')

        # Good!  Create a token, give to the user
        token = models.Token(
            id=util.gen_random(20),
            user=user,
            timestamp=datetime.utcnow()
        )

        # Need to use force_insert since the primary key is not an integer.
        token.save(force_insert=True)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'token': token.id})


class BillResource(BaseResource):
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'id': 'foo'})


class BillInfoResource(BaseResource):
    def on_get(self, req, resp, bill_id):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'info': 'foo'})


class BillItemsResource(BaseResource):
    def on_post(self, req, resp, bill_id):
        pass

    def on_get(self, req, resp, bill_id):
        pass


class BillSingleItemResource(BaseResource):
    def on_delete(self, req, resp, bill_id, item_id):
        pass


class BillConfirmResource(BaseResource):
    def on_post(self, req, resp, bill_id):
        pass


class BillQrResource(BaseResource):
    def on_get(self, req, resp, bill_id):
        pass


api = app = falcon.API(before=[auth, check_media_type])
db = models.bind_db(config.get_db())
db.connect()

opts = {
    'db': db,
}

api.add_route('/login', AuthenticateRoute(**opts))
api.add_route('/bills', BillResource(**opts))
api.add_route('/bills/{bill_id}', BillInfoResource(**opts))
api.add_route('/bills/{bill_id}/items', BillItemsResource(**opts))
api.add_route('/bills/{bill_id}/items/{item_id}', BillSingleItemResource(**opts))
api.add_route('/bills/{bill_id}/confirm', BillConfirmResource(**opts))
api.add_route('/bills/{bill_id}/qr', BillQrResource(**opts))
