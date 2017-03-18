from flask import Flask
from flask_bootstrap import Bootstrap
import json
from config import DB_FILE_PATH, DB_INIT_URLS_LIST

app = Flask(__name__)
Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True


class DbJson:

    def __init__(self, file_name):
        self.file_name = file_name
        self.db_json_dict = {}
        try:
            with open(file_name, 'r') as f_to_read_json:
                self.db_json_dict = json.loads(f_to_read_json.read())
        except FileNotFoundError:
            pass
        self._current_id = max([0] + [int(k) for k in self.db_json_dict.keys()])

    # only markdown is returned
    def __getitem__(self, image_id):
        return self.db_json_dict.get(str(image_id), {}).get('markdown', {})

    def get_full_item(self, image_id):
        return self.db_json_dict.get(str(image_id), {})

    # only markdown is set
    def __setitem__(self, key, value):
        if str(key) not in self.db_json_dict:
            self.db_json_dict[str(key)] = {'url': None}
        self.db_json_dict[str(key)].update({"markdown": value})
        self.save()

    def generate_next_id(self):
        new_id = self._current_id
        self._current_id += 1
        return new_id

    def all(self):
        return self.db_json_dict

    def save(self):
        with open(DB_FILE_PATH, 'w') as f:
            print(json.dumps(self.db_json_dict), file=f)

    def init_from_urls(self, file_path):
        current_urls = set([self.db_json_dict[key].get('url', None) for key in self.db_json_dict])
        with open(file_path, 'r') as f:
            for line in f.readlines():
                if line in current_urls:
                    continue
                new_image_id = self.generate_next_id()
                self.db_json_dict[str(new_image_id)] = {"url": line.strip()}


db = DbJson(DB_FILE_PATH)
db.init_from_urls(DB_INIT_URLS_LIST)

from app.models import ImagesToMark
images = ImagesToMark()

from app.controllers import main_page_module

app.register_blueprint(main_page_module)
