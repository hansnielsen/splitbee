import os
import six
import bcrypt
import falcon
import requests
from functools import wraps
from datetime import datetime
from voluptuous import Schema, MultipleInvalid

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
    token_given = req.get_header('X-Auth-Token')
    if token_given is None:
        raise falcon.HTTPUnauthorized('Auth token required',
                                      'Please provide a valid auth token as '
                                      'part of the request.')

    # Fetch the token.
    try:
        token = models.Token.get(models.Token.id == token_given)
    except models.Token.DoesNotExist:
        raise falcon.HTTPUnauthorized('Auth token required',
                                      'Please provide a valid auth token as '
                                      'part of the request.')

    # Validate the timestamp on the token.  Note that we can provide a 'real'
    # error message here, as opposed to the above, since it should be hard for
    # a malicious user to obtain any token, even an expired one.
    time_diff = (datetime.utcnow() - token.timestamp).total_seconds()
    if time_diff > 1 * 60 * 60:
        raise falcon.HTTPUnauthorized('Auth token required',
                                      'Token has expired.')

    # We save the user model for use in the request handler.
    req.env['splitbee.user'] = token.user


def check_media_type(req, resp, params):
    if not req.client_accepts_json:
        raise falcon.HTTPUnsupportedMediaType(
            'Media type not supported',
            'This API only supports the JSON media type.')


def set_headers(req, resp, params):
    # TODO: set headers for CORS?
    req.set_header('X-UA-Compatible', 'IE=Edge')
    pass


def with_schema(*args, **kwargs):
    """
    This decorator makes writing functions that just load JSON, validate the
    contents, and then do something easier.  It will effectively::
        1. Load the request's body as JSON.
        2. Validate the JSON according to the given schema
        3. Call the original function with an additional keyword argument of
           'body', set to the parsed and validated JSON.
    """
    # Require everything.
    kwargs['required'] = True
    schema = Schema(*args, **kwargs)

    def decorator(func):
        @wraps(func)
        def wrapped(self, req, resp, *args, **kwargs):
            # Load the body as JSON.
            try:
                params = json.loads(req.stream.read())
            except ValueError:
                raise falcon.HTTPBadRequest('Invalid JSON',
                                            'Could not deserialize the request'
                                            ' body as JSON')

            # Validate it.
            try:
                validated = schema(params)
            except MultipleInvalid as e:
                raise falcon.HTTPBadRequest(
                    'Invalid argument(s)',
                    str(e)
                )

            # Call the original function
            kwargs['body'] = validated
            return func(self, req, resp, *args, **kwargs)

        return wrapped

    return decorator


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
    @with_schema({
        'user': six.string_types[0],
        'password': six.string_types[0],
    })
    def on_post(self, req, resp, body):
        user_given = body['user']
        password = body['password']
        if isinstance(password, six.text_type):
            password = password.encode('utf-8')

        try:
            user = models.User.get(models.User.email == user_given)
        except models.User.DoesNotExist:
            raise falcon.HTTPBadRequest('Bad username or password',
                                        'A bad username or password was given.')

        # Hash and compare password - need to use constant-time compare here.
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
    @with_schema({
    })
    def on_post(self, req, resp, body):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({
            'user_id': req.env['splitbee.user'].id,
            'user_email': req.env['splitbee.user'].email,
        })


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
