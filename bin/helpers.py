import re
from config.config import PATH_TO_MESSAGES_FOLDER

with open(f'./{PATH_TO_MESSAGES_FOLDER}/index-messages.html', encoding='windows-1251') as f:
    full_text = f.read()
    
ids = {}
for msg in re.finditer(re.compile(r'(?P<_id>-?\d+)/messages0.html">(?P<name>.*)</a>'), full_text):
    ids[msg.group('_id')] = msg.group('name')