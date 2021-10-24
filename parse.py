#!/usr/bin/env python3
import click, datetime, re, json, html
from tqdm import tqdm
from pathlib import Path

MESSAGE_RE = re.compile(r'<div class="message__header">'
                        r'(<a href="https://vk.com/(?P<sender_type>id|public|club)(?P<sender_id>\d+)">.+</a>)?'
                        r'(?P<sender_is_self>Вы)?'
                        r', (?P<date>.+?:\d\d:\d\d).*</div>\n'
                        r'  <div>(?P<text>.*)<div class="kludges">', re.MULTILINE)

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


def parse_ds(ds: str) -> datetime.datetime:
    for month in MONTHS:
        if month in ds:
            ds = ds.replace(month, MONTHS[month])
            break

    if len(ds.split()[0]) == 1:
        ds = '0' + ds

    return datetime.datetime.strptime(ds, '%d %m %Y в %X')


def parse_message(msg: re.Match, sender=None):
    if msg.group('sender_is_self'):
        sender_id = 'self'
    else:
        sender_id = msg.group('sender_id')
        if msg.group('sender_type') != 'id':
            sender_id = '-' + sender_id

    if sender is not None and sender_id != str(sender):
        return None

    text = msg.group('text')
    if not text:
        return None

    text = html.unescape(text).replace('<br>', '\n')

    return {'text': text,
            'timestamp': int(parse_ds(msg.group('date')).timestamp()),
            'sender': sender_id}


@click.command()
@click.argument('data_folder_path', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument('save_file_path', type=click.Path(dir_okay=False, path_type=Path))
@click.option('-s', '--sender', help='id отправителя сообщения, например 12345 или -12345 для сообществ. Для сохранения только собственных сообщений -s self')
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
            full_text = f.read()
        _peer_id = path.parts[-2]

        for msg in re.finditer(MESSAGE_RE, full_text):
            try:
                parsed = parse_message(msg, sender=sender)
            except Exception:
                print(msg.group(0))
                raise
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
