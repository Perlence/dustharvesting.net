import yaml
from flask import Flask, abort, render_template


app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.config['FREEZER_DESTINATION'] = '.'
app.config['FREEZER_DESTINATION_IGNORE'] = '*'
app.config['FREEZER_STATIC_IGNORE'] = '*'


@app.route('/')
@app.route('/<name>')
def index(name='index'):
    try:
        with open(name + '.yaml', 'r', encoding='utf-8') as fp:
            data = yaml.safe_load(fp)
    except IOError:
        abort(404)
    return render_template(name + '.html', **data)


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
