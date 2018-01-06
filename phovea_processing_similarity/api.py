from __future__ import absolute_import
from phovea_server.ns import Namespace
from . import tasks  # import from current package
from flask import request

app = Namespace(__name__)


@app.route('/column/<method>/', methods=['GET'])
def calc_similarity(method):
  res = tasks.column_similarity.delay(method, request.args['range'])
  return res.id


@app.route('/group/<method>/', methods=['GET'])
def calc_similarity(method):
  res = tasks.group_similarity.delay(method, request.args['range'])
  return res.id


def create():
  """
   entry point of this plugin
  """
  return app
