from flask import Flask
from flask_bootstrap import Bootstrap
import json

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

    def __getitem__(self, item):
        return self.db_json_dict.get(str(item), {})

    def __setitem__(self, key, value):
        self.db_json_dict[str(key)] = value
        with open('saved_markdowns.json', 'w') as f:
            json.dump(self.db_json_dict, f)

    def all(self):
        return self.db_json_dict

db = DbJson('saved_markdowns.json')

from app.models import ImagesToMark
images = ImagesToMark()

from app.controllers import main_page_module

app.register_blueprint(main_page_module)
