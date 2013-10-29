import os
import falcon

from . import json
from . import models


our_dir = os.path.abspath(os.path.dirname(__file__))
static_dir  = os.path.abspath(os.path.join(our_dir, '..', 'static'))


class BaseResource(object):
    def __init__(self, db):
        self.db = db


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


api = app = falcon.API()

# Options passed to construct each resource.
opts = {
    'db': None,
}

api.add_route('/bills', BillResource(opts))
api.add_route('/bills/{bill_id}', BillInfoResource(opts))
api.add_route('/bills/{bill_id}/items', BillItemsResource(opts))
api.add_route('/bills/{bill_id}/items/{item_id}', BillSingleItemResource(opts))
api.add_route('/bills/{bill_id}/confirm', BillConfirmResource(opts))
api.add_route('/bills/{bill_id}/qr', BillQrResource(opts))
