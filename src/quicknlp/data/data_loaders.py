from typing import List, Optional, Callable

from torchtext.data import Dataset, BucketIterator

from quicknlp.data.iterators import HierarchicalIterator


class S2SModelLoader:
    """Instance of ModelLoader. It is an iterator that buckets the data in batches of similar sizes based on
       a sort_key and iterates through the batches.

    """

    def __init__(self, dataset: Dataset, batch_size: int, source_names: List[str], target_names: List[str],
                 sort_key: Optional[Callable] = None, **kwargs):
        self.dataset = dataset
        self.source_names = source_names
        self.target_names = target_names
        # sort by the first field if no sort key is given
        if sort_key is None:
            sort_key = lambda x: getattr(x, self.source_names[0])
        self.dl = BucketIterator(dataset, batch_size=batch_size, sort_key=sort_key, **kwargs)
        self.bs = batch_size
        self.iter = 0

    def __iter__(self):
        self.iter = 0
        for batch in self.dl:
            if self.iter >= len(self): raise StopIteration
            source = [getattr(batch, name) for name in self.source_names]
            # target should start from the second token for S2S
            target = [getattr(batch, name)[1:] for name in self.target_names]
            yield source + target
            self.iter += 1

    def __len__(self):
        """number of batches to go through all the data"""
        return len(self.dl)


class HierarchicalModelLoader:
    """Loads Hierarchical data into batches, including source and target"""

    def __init__(self, dataset: Dataset, batch_size: int, target_names: List[str],
                 sort_key: Optional[Callable] = None, **kwargs):
        self.dataset = dataset
        self.target_names = target_names if isinstance(target_names, list) else [target_names]
        # sort by the first field if no sort key is given
        if sort_key is None:
            # The default sorting is done by conversation length
            sort_key = lambda x: len(x.roles)
        self.dl = HierarchicalIterator(dataset, batch_size=batch_size, sort_key=sort_key, **kwargs)
        self.bs = batch_size
        self.iter = 0

    def __iter__(self):
        self.iter = 0
        for batch in self.dl:
            if self.iter >= len(self): raise StopIteration
            yield [batch.context, batch.response]
            self.iter += 1

    def __len__(self):
        """number of batches to go through all the data"""
        return len(self.dl)