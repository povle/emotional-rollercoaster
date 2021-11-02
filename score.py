#!/usr/bin/env python3
import orjson as json
import os
import click
from tqdm import tqdm
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel, FastTextToxicModel
from dostoevsky.data import DataDownloader, DATA_BASE_PATH, AVAILABLE_FILES
from pathlib import Path
from functools import lru_cache

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

@lru_cache
def get_positivity_model():
    download_model('fasttext-social-network-model')
    return FastTextSocialNetworkModel(tokenizer=RegexTokenizer())

@lru_cache
def get_toxicity_model():
    download_model('fasttext-toxic-model')
    return FastTextToxicModel(tokenizer=RegexTokenizer())

def score_positivity(txt: str, model=None) -> float:
    if model is None:
        model = get_positivity_model()
    results = model.predict([txt], k=-1)
    return results[0]['positive'] - results[0]['negative']

def score_toxicity(txt: str, model=None) -> float:
    if model is None:
        model = get_toxicity_model()
    results = model.predict([txt], k=-1)
    return results[0]['toxic'] - results[0]['normal']


MODEL = {'positive': get_positivity_model, 'toxic': get_toxicity_model}
SCORE = {'positive': score_positivity, 'toxic': score_toxicity}


@click.command()
@click.argument('data_path', type=click.Path(dir_okay=False, path_type=Path))
@click.argument('save_path', type=click.Path(dir_okay=False, path_type=Path))
@click.option('-p',
              '--peer_id',
              help='id беседы сообщения, для личных диалогов равен id другого человека. '
                   'Для групповых чатов можно вводить id как в ссылке, например c31')
@click.option('-s',
              '--sender',
              default='self',
              help='id отправителя сообщения, например 12345 или -12345 для сообществ. '
                   'По умолчанию анализируются только собственные сообщения. '
                   'Чтобы проанализировать все, используйте -s all')
@click.option('-m',
              '--model',
              type=click.Choice(['positive', 'toxic'], case_sensitive=False),
              default='positive',
              help='Тип используемой модели. '
                   'По умолчанию positive - определяет позитивность сообщений. '
                   'toxic определяет токсичность.')
def score(data_path: Path, save_path: Path, peer_id: str = None, sender='self', model='positive'):
    # для диалогов
    if peer_id and peer_id.startswith('c'):
        peer_id = str(int(peer_id[1:])+2000000000)

    with data_path.open(encoding='utf8') as f:
        messages = [x for x in json.loads(f.read())
                    if (sender == 'all' or x['sender'] == sender)
                    and (peer_id is None or x['peer_id'] == peer_id)]

    dost_model = MODEL[model]()
    score = SCORE[model]

    def predict(txt: str):
        return score(txt, dost_model)

    scores = {}
    for msg in tqdm(messages):
        ts = msg['timestamp']
        scores[ts] = [str(predict(msg['text'])), str(msg['peer_id']), str(msg['sender'])] # TBD: переделать костыль

    with save_path.open('w', encoding='utf8') as f:
        for ts in sorted(scores):
            f.write(f"{ts},{', '.join(scores[ts])}\n") # TBD: переделать костыль


if __name__ == '__main__':
    score()
