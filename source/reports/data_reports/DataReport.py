from abc import ABC

from source.data_model.dataset.RepertoireDataset import RepertoireDataset
from source.reports.Report import Report


class DataReport(Report, ABC):

    def __init__(self, dataset: RepertoireDataset = None, path: str = None):
        self.dataset = dataset
        self.path = path

    pass
