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
@click.option('-s', '--sender', help='id отправителя сообщения, например 12345 или -12345 для сообществ. Для анализа только собственных сообщений -s self')
def score(data_path: Path, save_path: Path, sender: str = None):
    with data_path.open(encoding='utf8') as f:
        messages = [x for x in json.load(f) if sender is None or x['sender'] == sender]

    scores = {}
    for msg in tqdm(messages):
        ts = msg['timestamp']
        results = model.predict([msg['text']], k=-1)
        scores[ts] = results[0]['positive'] - results[0]['negative']

    with save_path.open('w', encoding='utf8') as f:
        for ts in sorted(scores):
            f.write(f'{ts},{scores[ts]}\n')


if __name__ == '__main__':
    score()
