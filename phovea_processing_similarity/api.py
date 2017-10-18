from __future__ import absolute_import
from phovea_server.ns import Namespace


app = Namespace(__name__)


@app.route('/similarity/<method>/', methods=['GET'])
def calc_similarity(method):
  from . import tasks  # import from current package
  from flask import request

  res = tasks.similarity.delay(method, request.args['range'])
  return res.id


def create():
  """
   entry point of this plugin
  """
  return app
