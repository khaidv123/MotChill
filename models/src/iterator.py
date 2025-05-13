import numpy as np
import math
import torch
import pandas as pd


class ReviewsIterator:
    def __init__(self, X, y, batch_size=32, shuffle=True):
        if isinstance(X, pd.DataFrame):
            X = X.values
        y = np.asarray(y)

        if shuffle:
            index = np.random.permutation(X.shape[0])
            X, y = X[index], y[index]

        self.X = X
        self.y = y
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.n_batches = int(math.ceil(X.shape[0] / batch_size))
        self._current = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self._current >= self.n_batches:
            raise StopIteration()
        k = self._current
        self._current += 1
        bs = self.batch_size
        return self.X[k * bs : (k + 1) * bs], self.y[k * bs : (k + 1) * bs]


def batches_train(X, y, bs=32, shuffle=True):
    for xb, yb in ReviewsIterator(X, y, bs, shuffle):
        xb = torch.LongTensor(xb)
        yb = torch.FloatTensor(yb)
        yield xb, yb.view(-1, 1)


def batches_recommend(X, y, bs=32, shuffle=True):
    for xb, yb in ReviewsIterator(X, y, bs, shuffle):
        xb = torch.LongTensor(xb.long())
        yb = torch.FloatTensor(yb)
        yield xb, yb.view(-1, 1)