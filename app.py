import codecs
from collections import OrderedDict

import flask
import yaml
import yaml.constructor

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

app = flask.Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

@app.route('/<name>')
def index(name='index'):
    data = yaml.load(open(name + '.yaml'), OrderedDictLoader)
    output = flask.render_template(name + '.html', **data)
    with codecs.open(name + '.html', 'w', encoding='utf-8') as fp:
        fp.write(output)
    return output

@app.context_processor
def helpers():
    def static(filename):
        return flask.url_for('static', filename=filename)

    def format_time(time):
        return '{}:{:02}'.format(*time)

    def album_length(album):
        lengths = album['tracks'].values()
        minutes, seconds = zip(*lengths)
        full_length = sum(minutes) * 60 + sum(seconds)
        return format_time((full_length // 60, full_length % 60))
    
    return dict(**locals())

if __name__ == '__main__':
    app.run('127.0.0.1', 8000, debug=True)
