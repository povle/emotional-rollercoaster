#!/usr/bin/env python3
import click, datetime, bs4, re, json, cchardet
from tqdm import tqdm
from bs4 import BeautifulSoup
from pathlib import Path


MONTHS = {'янв': '01',
          'фев': '02',
          'мар': '03',
          'апр': '04',
          'мая': '05',
          'июн': '06',
          'июл': '07',
          'авг': '08',
          'сен': '09',
          'окт': '10',
          'ноя': '11',
          'дек': '12'}


def parse_header(header: str) -> datetime.datetime:
    ds = header.replace('Вы', '')
    ds = ds.replace(', ', '')
    for month in MONTHS:
        if month in ds:
            ds = ds.replace(month, MONTHS[month])
            break

    if len(ds.split()[0]) == 1:
        ds = '0' + ds

    return datetime.datetime.strptime(ds, '%d %m %Y в %X')


def parse_message(msg, sender=None):
    header = msg.find(class_='message__header').contents
    if isinstance(header[0], bs4.element.NavigableString):
        dt_header = header[0]
        sender_id = 'self'
    else:
        dt_header = header[1]
        try:
            r = re.search(r'(id|public|club)(\d+)"', str(header[0]))
            sender_id = r.group(2)
            if r.group(1) == 'public':
                sender_id = '-' + sender_id
        except Exception:
            print(str(msg))
            raise

    if sender is not None and sender_id != str(sender):
        return None

    kludges = msg.find(class_='kludges')
    if kludges is None:
        return None

    if not isinstance(kludges.parent.contents[0], bs4.element.NavigableString):
        return None

    return {'text': kludges.parent.contents[0],
            'timestamp': int(parse_header(dt_header).timestamp()),
            'sender': sender_id}


@click.command()
@click.argument('data_folder_path', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument('save_file_path', type=click.Path(dir_okay=False, path_type=Path))
@click.option('-s', '--sender', help='id отправителя сообщения, например 12345 или -12345 для сообществ')
@click.option('-f', '--save_freq', type=int, help='частота сохранения файла (если не установлена то файл сохраняется только после обработки всех сообщений)')
@click.option('-p', '--peer_id', default='*', help='id беседы сообщения, для личных диалогов равен id другого человека')
def parse_messages(data_folder_path: Path,
                   save_file_path: Path = None,
                   sender=None,
                   save_freq: int = None,
                   peer_id='*'):
    data = []

    for n, path in enumerate(tqdm(list(data_folder_path.glob(f'{peer_id}/*.html')))):
        with open(path, encoding='windows-1251') as f:
            soup = BeautifulSoup(f, 'lxml')

        message_list = soup.findAll(class_='item')

        _peer_id = path.parts[-2]

        for msg in message_list:
            parsed = parse_message(msg, sender=sender)
            if parsed is not None:
                parsed['peer_id'] = _peer_id
                data.append(parsed)

        if (save_freq is not None) and (save_file_path is not None) and (n % save_freq == 0):
            with save_file_path.open('w') as f:
                json.dump(data, f, ensure_ascii=False)

    if save_file_path is not None:
        with save_file_path.open('w') as f:
            json.dump(data, f, ensure_ascii=False)

    return data


if __name__ == '__main__':
    parse_messages()
