from __future__ import absolute_import

from phovea_processing_queue.task_definition import task, getLogger
from phovea_server.dataset import list_datasets
from .similarity import similarity_by_name
import numpy as np

_log = getLogger(__name__)


def list_groups():
  groups = []

  for dataset in list_datasets():
    # check data type, e.g. HDFTable, HDFStratification, HDFMatrix
    if dataset.type == 'stratification':
      for group in dataset.groups():
        groups.append(dict(
          dataset=dataset.id,
          label=group.name,
          ids=dataset.rowids(group.range)
        ))
    elif dataset.type == 'matrix' and dataset.value == 'categorical':  # some matrices has no categories (mRNA, RPPA)
      mat_data = dataset.asnumpy()
      # datatset.cols() are the stuff that can be in added to stratomex
      for col in range(mat_data.shape[1]):  # iterate over columns (numbers)
        mat_column = mat_data[:, col]  # get column
        # check in which categories the patients are
        for cat in dataset.categories:
          # get indicies as 1-column matrix and convert to 1d array:
          cat_row_indicies = np.argwhere(mat_column == cat['name'])[:, 0]
          groups.append(dict(
            dataset=dataset.id + '-c' + str(col),
            label=cat if isinstance(cat, str) else cat['label'],
            ids=dataset.rowids()[cat_row_indicies]
          ))
    elif dataset.type == 'table':  # has no 'value'-attribute like matrix
      for col in dataset.columns:
        if col.type == 'categorical':
          col_data = col.asnumpy()  # table doesnt have asnumpy()
          for cat in col.categories:
            # TCGA table had just the strings, calumma table has a dict like matrix above
            cat_name = cat if isinstance(cat, str) else cat['name']
            cat_row_indicies = np.argwhere(col_data == cat_name)[:, 0]
            if cat_row_indicies.size > 0:
              groups.append(dict(
                # id in stratomex has trailing '-s' which is not needed here
                # (e.g. tcgaGbmSampledClinical_patient.ethnicity-s)
                dataset=dataset.id + '_' + col.name,
                label=cat if isinstance(cat, str) else cat['label'],
                ids=dataset.rowids()[cat_row_indicies]
              ))

  return groups


@task
def add(x, y):
  return x + y


@task
def group_similarity(method, ids):
  _log.debug('Start to calculate %s similarity.', method)

  similarity_measure = similarity_by_name(method)
  if similarity_measure is None:
    raise ValueError("No similarity measure for given method: " + method)

  result = {'values': {}, 'groups': {}}

  try:
    from phovea_server.range import parse
    parsed_range = parse(ids)
    cmp_patients = np.array(parsed_range[0])  # [0] since ranges are multidimensional but you just want the first one
    # now compare that group's list of patients to all others

    # categorized data:
    # for group in list_groups():
    #   sim_score = similarity_measure(cmp_patients, group['ids'])
    #   if group['dataset'] not in result["values"] or similarity_measure.is_more_similar(sim_score,
    #                                                                                   result['values'][group['dataset']]):
    #     result['values'][group['dataset']] = sim_score
    #     result['groups'][group['dataset']] = group['label']

    # numerical data:
    # numerical data is binned to find best match
    for dataset in list_datasets():
      if dataset.type == 'table':  # maybe also vector?
        print dataset.id
        for col in dataset.columns:
          if col.type == 'real'or col.type == 'int':
            # real and int is numerical
            data_stack = np.column_stack((dataset.rowids(),col.asnumpy(), np.zeros(dataset.rowids().shape[0])))  # concat ids an data
            # matrix is now sorted by id, not by data
            data_stack = data_stack[data_stack[:,1].argsort()]  # sort by data
            ids_found = 0;
            for row in range(data_stack.shape[0]):  # iterate over columns (numbers)
              if data_stack[row][0] in cmp_patients:
                ids_found += 1
              data_stack[row][2] = ids_found

            print col.name




  except Exception as e:
    _log.exception('Can not fulfill task. Error: %s.', e)
    raise  # rejects promise

  return result  # to JSON automatically
