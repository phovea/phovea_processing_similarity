import abc
import numpy as np
from scipy import stats


__author__ = 'Klaus Eckelt'


def similarity_by_name(method_name):
  for sim_measure in ASimilarityMeasure.__subclasses__():
    if sim_measure.matches(method_name):
      return sim_measure()


class ASimilarityMeasure(object, metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def __call__(self, set_a, set_b):
    pass

  @staticmethod
  @abc.abstractmethod
  def is_more_similar(measure_a, measure_b):
    return measure_a > measure_b  # higher similarity score = better

  @staticmethod
  @abc.abstractmethod
  def matches(name):
    return False


class JaccardSimilarity(ASimilarityMeasure):
  def __call__(self, set_a, set_b):
    # set_a and set_b are ids of elements
    return np.intersect1d(set_a, set_b).size / np.union1d(set_a, set_b).size  # independent of parameter order

  @staticmethod
  def matches(name):
    return "jaccard" == name


class PercentAinB(ASimilarityMeasure):
  def __call__(self, set_a, set_b):
    # set_a and set_b are ids of elements
    return np.intersect1d(set_a, set_b).size / set_a.size  # independent of parameter order

  @staticmethod
  def matches(name):
    return "ainb" == name


class PercentBinA(ASimilarityMeasure):
  def __call__(self, set_a, set_b):
    # set_a and set_b are ids of elements
    return np.intersect1d(set_a, set_b).size / set_b.size  # independent of parameter order

  @staticmethod
  def matches(name):
    return "bina" == name


class Pearson(ASimilarityMeasure):
  def __call__(self, set_a, set_b):
    # Assume set_a and set_b are numerical values
    if set_a.shape[0] != set_b.shape[0]:
      return np.nan
    else:
      # if all values are 0 -> divide by 0 --> the coefficient gets NaN  --> null in json
      (pearson_correlation, p_value) = stats.pearsonr(
        np.nan_to_num(np.array(set_a, dtype=np.float)),
        np.nan_to_num(np.array(set_b, dtype=np.float))
      )
      # p-value is currently unuused
      return pearson_correlation

  @staticmethod
  def matches(name):
    return "pearson" == name

  @staticmethod
  def is_more_similar(measure_a, measure_b):
    return abs(measure_a) > abs(measure_b)  # more correlation (positive or negative) = more similary
