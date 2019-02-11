#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, g, abort
import ConfigParser
import os

import tplight

Config = ConfigParser.ConfigParser()
Config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))

app = Flask(__name__, static_folder='web/static', template_folder='web/templates')
light = tplight.LB130(Config.get('main', 'bulb_address'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/do_cmd', methods=['POST'])
def do_cmd():
    if app.debug:
        print('do_cmd data: ' + str(request.data))
    xhr_dict = request.get_json(force=True)
    if not isinstance(xhr_dict, dict) or 'cmd' not in xhr_dict:
        abort(400)

    light_method = getattr(light, xhr_dict['cmd'], None)
    if light_method is None:
        abort(400)

    arg = xhr_dict.get('arg', None)
    kwargs = xhr_dict.get('kwargs', {})
    if arg is not None and arg.isdigit():
        arg = int(arg)

    if isinstance(getattr(type(light), xhr_dict['cmd']), property):
        if arg is not None:
            setattr(light, xhr_dict['cmd'], arg)
            res = 'OK'
        else:
            res = light_method
    else:
        if arg is not None:
            res = light_method(arg, **kwargs)
        else:
            res = light_method(**kwargs)
        if res is None:
            res = 'OK'
    return jsonify(result=res)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(Config.get('main', 'listen_port')))
