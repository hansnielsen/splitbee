import os
import falcon

from . import json


our_dir = os.path.abspath(os.path.dirname(__file__))
static_dir  = os.path.abspath(os.path.join(our_dir, '..', 'static'))


class BillResource(object):
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'id': 'foo'})


class BillInfoResource(object):
    def on_get(self, req, resp, bill_id):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'info': 'foo'})


class BillItemsResource(object):
    def on_post(self, req, resp, bill_id):
        pass

    def on_get(self, req, resp, bill_id):
        pass


class BillSingleItemResource(object):
    def on_delete(self, req, resp, bill_id, item_id):
        pass


class BillConfirmResource(object):
    def on_post(self, req, resp, bill_id):
        pass


class BillQrResource(object):
    def on_get(self, req, resp, bill_id):
        pass


api = app = falcon.API()

api.add_route('/bills', BillResource())
api.add_route('/bills/{bill_id}', BillInfoResource())
api.add_route('/bills/{bill_id}/items', BillItemsResource())
api.add_route('/bills/{bill_id}/items/{item_id}', BillSingleItemResource())
api.add_route('/bills/{bill_id}/confirm', BillConfirmResource())
api.add_route('/bills/{bill_id}/qr', BillQrResource())
