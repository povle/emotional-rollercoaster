#!/usr/bin/env python3
import json
import os
import click
from tqdm import tqdm
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.data import DataDownloader, DATA_BASE_PATH, AVAILABLE_FILES
from pathlib import Path

def download_model(model: str):
    downloader = DataDownloader()
    if model not in AVAILABLE_FILES:
        raise ValueError(f'Unknown package: {model}')
    source, destination = AVAILABLE_FILES[model]
    destination_path: str = os.path.join(DATA_BASE_PATH, destination)
    if os.path.exists(destination_path):
        return
    downloader.download(source=source, destination=destination)


download_model('fasttext-social-network-model')
model = FastTextSocialNetworkModel(tokenizer=RegexTokenizer())


@click.command()
@click.argument('data_path', type=click.Path(dir_okay=False, path_type=Path))
@click.argument('save_path', type=click.Path(dir_okay=False, path_type=Path))
def score(data_path: Path, save_path: Path):
    with data_path.open() as f:
        messages = json.load(f)

    scores = {}
    for msg in tqdm(messages):
        ts = msg['timestamp']
        results = model.predict([msg['text']], k=-1)
        scores[ts] = results[0]['positive'] - results[0]['negative']

    with save_path.open('w') as f:
        for ts in sorted(scores):
            f.write(f'{ts},{scores[ts]}\n')


if __name__ == '__main__':
    score()
