from __future__ import absolute_import, division

from phovea_processing_queue.task_definition import task, getLogger
from phovea_server.dataset import list_datasets, get as get_dataset
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


def list_columns():
  columns = []

  # columns {
  #   id  (full id)
  #   type (categorical, real, int, string, ...)  (not dataset's type but the column's
  #   rowids

  #   groups {
  #     label
  #     ids --> from rowIds
  #   }
  # }

  #for dataset in list_datasets():
    # check data type, e.g. HDFTable, HDFStratification, HDFMatrix
   # if dataset.type == 'stratification':
   # elif dataset.type == 'matrix':
   # elif dataset.type == 'table':  # has no 'value'-attribute like matrix


  return columns

@task
def column_similarity(method, column_id):
  _log.debug('Start to calculate %s similarity.', method)

  similarity_measure = similarity_by_name(method)
  if similarity_measure is None:
    raise ValueError("No similarity measure for given method: " + method)


  # result
  # -- dataset_id =
  # -- -- similarity score
  # -- dataset_id
  # -- -- similarity score
  # an so on
  result = {}

  try:
    given_columns_values = np.array([])

    # find given column
    for dataset in list_datasets():
      if dataset.type == 'table':  # maybe also vector?
        for col in dataset.columns:
          if col.type == 'real' or col.type == 'int':
            # real and int is numerical
            col_id = dataset.id + '_' + col.name
            if col_id == column_id:
              given_columns_values = col.asnumpy()

    # compare given column
    if given_columns_values.shape > 0:
      for dataset in list_datasets():
        if dataset.type == 'table':  # maybe also vector?
          for col in dataset.columns:
            if col.type == 'real' or col.type == 'int':
              other_values = col.asnumpy()
              result[dataset.id + '_' + col.name] = similarity_measure(given_columns_values, other_values)

  except Exception as e:
    _log.exception('Can not fulfill task. Error: %s.', e)
    raise  # rejects promise

  return result  # to JSON automatically


@task
def group_similarity(method, ids):
  _log.debug('Start to calculate %s similarity.', method)

  similarity_measure = similarity_by_name(method)
  if similarity_measure is None:
    raise ValueError("No similarity measure for given method: " + method)

  result = {'values': {}, 'groups': {}, 'threshold': {}}

  try:
    from phovea_server.range import parse
    parsed_range = parse(ids)
    cmp_patients = np.array(parsed_range[0])  # [0] since ranges are multidimensional but you just want the first one
    # now compare that group's list of patients to all others

    # categorized data:
    for group in list_groups():
      sim_score = similarity_measure(cmp_patients, group['ids'])
      if group['dataset'] not in result["values"] or similarity_measure.is_more_similar(sim_score,
                                                                                        result['values'][
                                                                                        group['dataset']]):
        result['values'][group['dataset']] = sim_score
        result['groups'][group['dataset']] = group['label']

    # numerical data:
    # numerical data is binned to find best match
    for dataset in list_datasets():
      if dataset.type == 'table':  # maybe also vector?
        print dataset.id
        for col in dataset.columns:
          if col.type == 'real' or col.type == 'int':
            # real and int is numerical
            data_stack = np.column_stack(
              (dataset.rowids(), col.asnumpy(), np.zeros((dataset.rowids().shape[0], 4))))  # concat ids an data
            # matrix is sorted by id, not by data
            data_stack = data_stack[data_stack[:, 1].argsort()]  # sort by data
            ids_found = 0
            ids_present = np.sum(np.in1d(cmp_patients, dataset.rowids(), assume_unique=True))
            for row in range(data_stack.shape[0]):  # iterate over columns (numbers)
              ids_found_reverse = ids_present - ids_found
              data_stack[row][4] = ids_found_reverse
              # data_stack[row][5] = (ids_present - ids_found) / (row-ids_found+ids_present)  # not (row+1) here
              total_elements_reverse = ((data_stack.shape[0] - row) + ids_found)
              data_stack[row][5] = ids_found_reverse / total_elements_reverse
              if data_stack[row][0] in cmp_patients:
                ids_found += 1
              data_stack[row][2] = ids_found
              total_elements = ((row + 1) - ids_found + ids_present)  # +1 to reflect number of elements
              data_stack[row][3] = ids_found / total_elements

            print col.name
            # find maximum in frontwards and backwards scorses
            max_similarity = float(np.max(data_stack[:, [3, 5]]))
            print "highest similarity: " + str(max_similarity)
            # row 0, col 0 = index 0, row 0 col 1 = index 1 and so on --> divide by two to get row
            max_similarity_row = np.argmax(data_stack[:, [3, 5]]) / float(2)
            # print data_stack[max_similarity_row]

            # numerical value at maximum score = value to split
            # ordino will split in values <= threshold and values > thresold
            # so: if highest similarity is in forward group (no 0.5 remainder) -> use value
            # but: if highest similarity is in backward group (0.5 remainder) -> use next lower value

            split_reverse = max_similarity_row % 1 != 0  # second column will always have an odd index -> 0.5 remainder
            print "split at number: " + str(data_stack[max_similarity_row, [1]]) + \
                  (" from back" if split_reverse else " from front")

            num_to_split = data_stack[max_similarity_row - (1 if split_reverse else 0), 1]
            # casting none to float does not work
            # if the value is None (no value available) --> make a group with all available values (val <= max)
            # ordino will make another group with missing values itself
            num_to_split = float(num_to_split) if num_to_split is not None else np.max(data_stack[:,1])
            result['values'][dataset.id + '_' + col.name] = max_similarity
            result['groups'][dataset.id + '_' + col.name] = col.name + (" > " if split_reverse else " <= ") + str(num_to_split)
            result['threshold'][dataset.id + '_' + col.name] = [num_to_split]


  except Exception as e:
    _log.exception('Can not fulfill task. Error: %s.', e)
    raise  # rejects promise

  return result  # to JSON automatically
