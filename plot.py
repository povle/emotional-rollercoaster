#!/usr/bin/env python3
import matplotlib.pyplot as plt
import click
import pandas as pd
from pathlib import Path
from typing import Tuple


def load_scores(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, names=['datetime', 'score'], index_col='datetime')
    df.index = pd.to_datetime(df.index, unit='s')
    return df


@click.command()
@click.argument('data_paths', nargs=-1, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option('-w', '--width', type=int, default=5000)
def plot_moving_average(data_paths: Tuple[Path], width: int):
    single = len(data_paths) == 1

    ax = plt.gca()
    ax.xaxis.label.set_visible(False)

    for data_path in data_paths:
        df = load_scores(data_path)
        ax = df.rolling(width).mean().plot(ax=ax, legend=False)

    if single:
        plt.axhline(y=df['score'].mean(), color='r')
    plt.show()


if __name__ == '__main__':
    plot_moving_average()
