import abc

from source.data_model.dataset.RepertoireDataset import RepertoireDataset


class Preprocessor(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def process(dataset: RepertoireDataset, params: dict) -> RepertoireDataset:
        pass

    @abc.abstractmethod
    def process_dataset(self, dataset: RepertoireDataset) -> RepertoireDataset:
        pass
