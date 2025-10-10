from pathlib import Path
from folioforge.pipeline.protocol import PipelineExecutor
from folioforge.preprocessor.protocol import Preprocessor
from folioforge.extraction.protocol import Extractor
from folioforge.models.document import DocumentEntry, DocumentReference
from dask.distributed import Client
import dask.bag as db


def expand(r: DocumentReference) -> list[tuple[Path, DocumentEntry]]:
    return [(r.path, i) for i in r.items]


class DaskPipelineExecutor(PipelineExecutor):
    def __init__(
        self, preprocessors: list[Preprocessor], extractor: Extractor, n_workers: int = 4, threads_per_worker: int = 1, partitions: int = 2
    ) -> None:
        self.preprocessors = preprocessors
        self.extractor = extractor
        self.n_workers = n_workers
        self.threads_per_worker = threads_per_worker
        self.partitions = partitions

    @classmethod
    def setup(
        cls, preprocessors: list[Preprocessor], extractor: Extractor, n_workers: int = 4, threads_per_worker: int = 1, partitions: int = 2
    ) -> "DaskPipelineExecutor":
        return DaskPipelineExecutor(
            preprocessors, extractor, n_workers=n_workers, threads_per_worker=threads_per_worker, partitions=partitions
        )

    def extract(self, entry: tuple[Path, DocumentEntry]) -> tuple[Path, DocumentEntry]:
        return (entry[0], self.extractor.extract(entry[1]))

    def execute(self, paths: list[Path]) -> list[DocumentReference]:
        Client(n_workers=self.n_workers, threads_per_worker=self.threads_per_worker)
        references = db.from_sequence([DocumentReference(path, [], None) for path in paths], npartitions=self.partitions)

        for processor in self.preprocessors:
            references = db.map(processor.process, references)

        # turn into bag of document entries
        entries = references.map(expand).flatten().repartition(npartitions=self.partitions)
        entries = db.map(self.extract, entries)

        references = entries.groupby(lambda e: e[0]).map(
            lambda e: DocumentReference(e[0], [i[1] for i in e[1]], "\n\n".join(i[1].converted or "" for i in e[1]))
        )
        result = references.compute(retries=10)
        return result
