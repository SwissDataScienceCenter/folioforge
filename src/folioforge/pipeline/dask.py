import tempfile
from functools import partial
from pathlib import Path
from typing import TypeVar, cast

import dask.bag as db
from dask.distributed import Client

from folioforge.extraction.protocol import Extractor
from folioforge.models.document import DocumentEntry, DocumentReference
from folioforge.output.protocol import OutputGenerator
from folioforge.pipeline.protocol import PipelineExecutor
from folioforge.postprocessor.protocol import Postprocessor
from folioforge.preprocessor.protocol import Preprocessor


def expand(r: DocumentReference) -> list[tuple[Path, DocumentEntry]]:
    return [(r.path, i) for i in r.items]


T = TypeVar("T")


class DaskPipelineExecutor[T](PipelineExecutor):
    def __init__(
        self,
        preprocessors: list[Preprocessor],
        extractor: Extractor,
        format: OutputGenerator[T],
        postprocessors: list[Postprocessor] | None,
        outdir: Path,
        n_workers: int = 4,
        threads_per_worker: int = 1,
        partitions: int = 2,
    ) -> None:
        self.preprocessors = preprocessors
        self.extractor = extractor
        self.postprocessors = postprocessors
        self.format = format
        self.outdir = outdir
        self.n_workers = n_workers
        self.threads_per_worker = threads_per_worker
        self.partitions = partitions

        if not self.extractor.supports_pickle:
            raise NotImplementedError(f"The extractor {self.extractor} does not support pickling and can't use dask")

    @classmethod
    def setup(
        cls,
        preprocessors: list[Preprocessor],
        extractor: Extractor,
        format: OutputGenerator[T],
        postprocessors: list[Postprocessor] | None = None,
        outdir: Path | None = None,
        n_workers: int = 4,
        threads_per_worker: int = 1,
        partitions: int = 2,
    ) -> "DaskPipelineExecutor":
        if outdir is None:
            outdir = Path(tempfile.mkdtemp(prefix="folioforge"))
        return DaskPipelineExecutor(
            preprocessors,
            extractor,
            format,
            postprocessors,
            outdir,
            n_workers=n_workers,
            threads_per_worker=threads_per_worker,
            partitions=partitions,
        )

    def extract(self, entry: tuple[Path, DocumentEntry]) -> tuple[Path, DocumentEntry]:
        return (entry[0], self.extractor.extract(entry[1]))

    def execute(self, paths: list[Path]) -> T:
        Client(n_workers=self.n_workers, threads_per_worker=self.threads_per_worker)
        references = db.from_sequence(
            [DocumentReference(path=path, items=[], converted=None) for path in paths], npartitions=self.partitions
        )

        for processor in self.preprocessors:
            references = db.map(partial(processor.process, outdir=self.outdir), references)

        # turn into bag of document entries
        entries = references.map(expand).flatten().repartition(npartitions=self.partitions)
        entries = db.map(self.extract, entries)

        references = entries.groupby(lambda e: e[0]).map(
            lambda e: DocumentReference(path=e[0], items=[i[1] for i in e[1]], converted="\n\n".join(i[1].converted or "" for i in e[1]))
        )
        result = cast(list[DocumentReference], references.compute())
        if self.postprocessors:
            for postprocessor in self.postprocessors:
                result = postprocessor.process(result, self.outdir)

        return self.format.convert(result)
