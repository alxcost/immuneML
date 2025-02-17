import os
import shutil
from unittest import TestCase

from immuneML.caching.CacheType import CacheType
from immuneML.data_model.dataset.RepertoireDataset import RepertoireDataset
from immuneML.data_model.receptor.receptor_sequence.ReceptorSequence import ReceptorSequence
from immuneML.data_model.repertoire.Repertoire import Repertoire
from immuneML.environment.Constants import Constants
from immuneML.environment.EnvironmentSettings import EnvironmentSettings
from immuneML.environment.SequenceType import SequenceType
from immuneML.reports.data_reports.SequenceLengthDistribution import SequenceLengthDistribution
from immuneML.simulation.dataset_generation.RandomDatasetGenerator import RandomDatasetGenerator
from immuneML.util.PathBuilder import PathBuilder


class TestSequenceLengthDistribution(TestCase):

    def setUp(self) -> None:
        os.environ[Constants.CACHE_TYPE] = CacheType.TEST.name

    def test_get_normalized_sequence_lengths(self):
        path = PathBuilder.remove_old_and_build(EnvironmentSettings.tmp_test_path / "seq_len_rep")

        rep1 = Repertoire.build_from_sequence_objects(sequence_objects=[ReceptorSequence(amino_acid_sequence="AAA", identifier="1"),
                                                                        ReceptorSequence(amino_acid_sequence="AAAA", identifier="2"),
                                                                        ReceptorSequence(amino_acid_sequence="AAAAA", identifier="3"),
                                                                        ReceptorSequence(amino_acid_sequence="AAA", identifier="4")],
                                                      path=path, metadata={})
        rep2 = Repertoire.build_from_sequence_objects(sequence_objects=[ReceptorSequence(amino_acid_sequence="AAA", identifier="5"),
                                                                        ReceptorSequence(amino_acid_sequence="AAAA", identifier="6"),
                                                                        ReceptorSequence(amino_acid_sequence="AAAA", identifier="7"),
                                                                        ReceptorSequence(amino_acid_sequence="AAA", identifier="8")],
                                                      path=path, metadata={})

        dataset = RepertoireDataset(repertoires=[rep1, rep2])

        sld = SequenceLengthDistribution.build_object(dataset=dataset, sequence_type='amino_acid', result_path=path)

        result = sld.generate_report()
        self.assertTrue(os.path.isfile(result.output_figures[0].path))

        shutil.rmtree(path)

    def test_sequence_lengths_seq_dataset(self):
        path = PathBuilder.remove_old_and_build(EnvironmentSettings.tmp_test_path / "seq_len_seq")

        dataset = RandomDatasetGenerator.generate_sequence_dataset(50, {4: 0.33, 5: 0.33, 7: 0.33}, {}, path / 'dataset')

        sld = SequenceLengthDistribution(dataset, 1, path, sequence_type=SequenceType.AMINO_ACID)

        result = sld.generate_report()
        self.assertTrue(os.path.isfile(result.output_figures[0].path))

        shutil.rmtree(path)
