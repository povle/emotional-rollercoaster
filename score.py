#!/usr/bin/env python3
import orjson as json
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
    print('Загрузка языковой модели...')
    downloader.download(source=source, destination=destination)
    print('Загрузка завершена.')


download_model('fasttext-social-network-model')
model = FastTextSocialNetworkModel(tokenizer=RegexTokenizer())


@click.command()
@click.argument('data_path', type=click.Path(dir_okay=False, path_type=Path))
@click.argument('save_path', type=click.Path(dir_okay=False, path_type=Path))
@click.option('-p',
              '--peer_id',
              help='id беседы сообщения, для личных диалогов равен id другого человека')
@click.option('-s',
              '--sender',
              default='self',
              help='id отправителя сообщения, например 12345 или -12345 для сообществ.'
                   'По умолчанию анализируются только собственные сообщения,'
                   'чтобы проанализировать все используйте -s all')
def score(data_path: Path, save_path: Path, peer_id: str = None, sender='self'):
    with data_path.open(encoding='utf8') as f:
        messages = [x for x in json.loads(f.read())
                    if (sender == 'all' or x['sender'] == sender)
                    and (peer_id is None or x['peer_id'] == peer_id)]

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
