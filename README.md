# Emotional Rollercoaster
## Выгрузка сообщений
Сначала необходимо [выгрузить из ВК архив своих сообщений](https://vk.com/data_protection?section=rules&scroll_to_archive=1). Примерно через 3 часа этот архив можно будет скачать. Нужно его разархивировать.

## Парсинг
Нужно запустить `parse.py` с указанием на путь к папкн messages из архива и путь, по которому будут сохранены сообщения в формате json.

 Например:
```bash
python3 parse.py Archive/messages messages.json
```

У `parse.py` есть дополнительные опции, список можно посмотреть с помощью `python3 parse.py --help`

## Анализ
Нужно запустить `score.py` с указанием на путь к спарсенным сообщениям и путь для сохранения результатов сентимент анализа.
```bash
python3 score.py messages.json scores.csv
```
У скрипта есть аналогичные `parse.py` опции.
Первый запуск займет дольше остальных, потому что сначала скачается языковая модель (примерно 80 мегабайт).

## Визуализация
```bash
python3 plot.py scores.csv
```
У скрипта есть опция `-w`, регулирующая ширину скользящего среднего. По умолчанию `-w 5000`. Стоит поэкспериментировать с этой настройкой: при слишком большом значении теряется точность графика, при слишком маленьком теряется гладкость.
