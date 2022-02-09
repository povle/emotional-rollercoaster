#!/usr/bin/env python3
import matplotlib.pyplot as plt
import datetime
import numpy as np
import click
from pathlib import Path
from typing import Tuple


def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w


@click.command()
@click.argument('data_paths', nargs=-1, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-w', '--width', type=int, default=5000)
def plot_moving_average(data_paths: Tuple[Path], width: int):
    for data_path in data_paths:
        raw_x = []
        raw_y = []
        with data_path.open() as f:
            for line in f:
                a, b = line.split(',')
                raw_x.append(int(a))
                raw_y.append(float(b))

        x = [datetime.datetime.fromtimestamp(x) for x in moving_average(raw_x, width)]
        y = moving_average(raw_y, width)

        plt.plot(x, y)

    if len(data_paths) == 1:
        plt.axhline(y=sum(y)/len(y), color='r')
    plt.show()


if __name__ == '__main__':
    plot_moving_average()
