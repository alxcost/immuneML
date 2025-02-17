import os
import shutil
from unittest import TestCase

from immuneML.caching.CacheType import CacheType
from immuneML.data_model.dataset.RepertoireDataset import RepertoireDataset
from immuneML.environment.Constants import Constants
from immuneML.environment.EnvironmentSettings import EnvironmentSettings
from immuneML.preprocessing.filters.ClonesPerRepertoireFilter import ClonesPerRepertoireFilter
from immuneML.util.PathBuilder import PathBuilder
from immuneML.util.RepertoireBuilder import RepertoireBuilder


class TestClonesPerRepertoireFilter(TestCase):

    def setUp(self) -> None:
        os.environ[Constants.CACHE_TYPE] = CacheType.TEST.name

    def test_process(self):
        path = PathBuilder.build(EnvironmentSettings.tmp_test_path / "test/tmp/clones_per_repertoire_filter/")
        dataset = RepertoireDataset(repertoires=RepertoireBuilder.build([["ACF", "ACF", "ACF"],
                                                                       ["ACF", "ACF"],
                                                                       ["ACF", "ACF", "ACF", "ACF"]], path)[0])

        dataset1 = ClonesPerRepertoireFilter(**{"lower_limit": 3, "result_path": path}).process_dataset(dataset, path)
        self.assertEqual(2, dataset1.get_example_count())

        dataset2 = ClonesPerRepertoireFilter(**{"upper_limit": 2, "result_path": path}).process_dataset(dataset, path)
        self.assertEqual(1, dataset2.get_example_count())

        self.assertRaises(AssertionError, ClonesPerRepertoireFilter(**{"lower_limit": 10, "result_path": path}).process_dataset, dataset, path)

        shutil.rmtree(path)
