import os
import codecs
from collections import OrderedDict

import yaml
import yaml.constructor
from jinja2 import Environment, FileSystemLoader

import helpers

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

template_dir = 'templates'

env = Environment(loader=FileSystemLoader(template_dir))
env.trim_blocks = True
env.lstrip_blocks = True

# Set functions starting with 'filter_' as jinja2 filters
for name in dir(helpers):
    if name.startswith('filter_'):
        env.filters[name.replace('filter_', '')] = getattr(helpers, name)

for template_name in os.listdir(template_dir):
    root, ext = os.path.splitext(template_name)
    data_name = root + '.yaml'
    template = env.get_template(template_name)
    data = yaml.load(open(data_name), OrderedDictLoader)
    data['helpers'] = helpers
    output = template.render(**data)
    with codecs.open(template_name, 'w', encoding='utf-8') as fp:
        fp.write(output)
