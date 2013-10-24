def filter_timeformat(value):
    return '{}:{:02}'.format(*value)

def album_length(album):
    lengths = album['tracks'].values()
    minutes, seconds = zip(*lengths)
    full_length = sum(minutes) * 60 + sum(seconds)
    return full_length // 60, full_length % 60
