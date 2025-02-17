import math
from pathlib import Path

import numpy as np

from immuneML.util.ReflectionHandler import ReflectionHandler


class ElementGenerator:

    def __init__(self, file_list: list, file_size: int = 1000, element_class_name: str = ""):
        self.file_list = file_list
        self.file_lengths = [-1 for _ in range(len(file_list))]
        self.file_size = file_size
        self.element_class_name = element_class_name

    def _load_batch(self, current_file: int):

        element_class = ReflectionHandler.get_class_by_name(self.element_class_name, "data_model")
        assert hasattr(element_class, 'create_from_record'), \
            f"{ElementGenerator.__name__}: cannot load the binary file, the class {element_class.__name__} has no 'create_from_record' method."

        try:
            elements = [element_class.create_from_record(el) for el in np.load(self.file_list[current_file], allow_pickle=False)]
        except ValueError as error:
            raise ValueError(f'{ElementGenerator.__name__}: an error occurred while creating an object from binary file. Details: {error}')

        return elements

    def _get_element_count(self, file_index: int):

        # TODO: make this abstract and move implementation to specific generator: count elements in file for new format

        if self.file_lengths[file_index] == -1:
            with self.file_list[file_index].open("rb") as file:
                count = len(np.load(file))
            self.file_lengths[file_index] = count

        return self.file_lengths[file_index]

    def get_element_count(self):
        for index in range(len(self.file_list)):
            if self.file_lengths[index] == -1:
                self._get_element_count(index)
        return sum(self.file_lengths)

    def build_batch_generator(self):
        """
        creates a generator which will return one batch of elements at the time

        :param batch_size: how many elements should be returned at once (default 1)
        :return: element generator
        """

        for current_file_index in range(len(self.file_list)):
            batch = self._load_batch(current_file_index)
            yield batch

    def build_element_generator(self):
        """
        creates a generator which will return one element at the time
        :return: element generator
        """
        for current_file_index in range(len(self.file_list)):
            batch = self._load_batch(current_file_index)
            for element in batch:
                yield element

    def make_subset(self, example_indices: list, path: Path, dataset_type: str, dataset_identifier: str):
        if example_indices is None or len(example_indices) == 0:
            raise RuntimeError(f"{ElementGenerator.__name__}: no examples were specified to create the dataset subset. "
                               f"Dataset type was {dataset_type}, dataset identifier: {dataset_identifier}.")
        batch_size = self.file_size
        elements = []
        file_count = 1

        example_indices.sort()

        batch_filenames = self._prepare_batch_filenames(len(example_indices), path, dataset_type, dataset_identifier)

        for index, batch in enumerate(self.build_batch_generator()):
            extracted_elements = self._extract_elements_from_batch(index, batch_size, batch, example_indices)
            elements.extend(extracted_elements)

            if len(elements) >= self.file_size or len(elements) == len(example_indices):
                self._store_elements_to_file(batch_filenames[file_count-1], elements[:self.file_size])
                file_count += 1
                elements = elements[self.file_size:]

        if len(elements) > 0:
            self._store_elements_to_file(batch_filenames[file_count - 1], elements)

        return batch_filenames

    def _prepare_batch_filenames(self, example_count: int, path: Path, dataset_type: str, dataset_identifier: str):
        batch_count = math.ceil(example_count / self.file_size)
        digits_count = len(str(batch_count)) + 1
        filenames = [path / f"{dataset_identifier}_{dataset_type}_batch{''.join(['0' for i in range(digits_count-len(str(index)))])}{index}.npy"
                     for index in range(batch_count)]
        return filenames

    def _store_elements_to_file(self, path, elements):
        if isinstance(elements, list) and len(elements) > 0:
            element_matrix = np.core.records.fromrecords([el.get_record() for el in elements], names=type(elements[0]).get_record_names())
            np.save(str(path), element_matrix, allow_pickle=False)

    def _extract_elements_from_batch(self, index, batch_size, batch, example_indices):
        upper_limit, lower_limit = (index + 1) * batch_size, index * batch_size
        batch_indices = [ind for ind in example_indices if lower_limit <= ind < upper_limit]

        assert len(batch_indices) == 0  or max(batch_indices) - lower_limit < len(batch), f"ElementGenerator: Found batch of size {len(batch)}, but expected {batch_size}. " \
                                                                                          f"Are the batch files sorted correctly? All files except the last file must have batch size {batch_size}."

        elements = [batch[i - lower_limit] for i in batch_indices]
        return elements
