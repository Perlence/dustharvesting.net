import os
import codecs
from collections import OrderedDict

import yaml
import yaml.constructor
from flask import Flask, abort, render_template, url_for, current_app

class OrderedDictLoader(yaml.Loader):
    '''A YAML loader that loads mappings into ordered dictionaries.
    '''
    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

@app.route('/')
@app.route('/<name>')
def index(name='index'):
    try:
        data = yaml.load(open(name + '.yaml'), OrderedDictLoader)
        output = render_template(name + '.html', **data)
        return output
    except IOError:
        abort(404)

@app.context_processor
def helpers():
    def format_time(time):
        return '{}:{:02}'.format(*time)

    def album_length(album):
        lengths = album['tracks'].values()
        minutes, seconds = zip(*lengths)
        full_length = sum(minutes) * 60 + sum(seconds)
        return format_time((full_length // 60, full_length % 60))

    def enumerate_links(links, lower=False):
        def html_link(args):
            text, link = args
            if lower:
                text = text.lower()
            return '<a href="{}">{}</a>'.format(link, text)
        return ', '.join(map(html_link, links.items()))
    
    return dict(**locals())

def freeze():
    from flask_frozen import Freezer
    freezer = Freezer(app)
    freezer.freeze()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'freeze':
        freeze()
    else:
        app.run(port=5000, debug=True)
