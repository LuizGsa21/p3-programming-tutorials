from datetime import datetime


def _convert_to_datetime(string):
    return datetime.strptime(string, '%b %d %Y %H:%M:%S')


_categories = [
    {'id': 1, 'name': 'Python'},
    {'id': 2, 'name': 'PHP'},
    {'id': 3, 'name': 'Java'},
    {'id': 4, 'name': 'HTML'},
    {'id': 5, 'name': 'CSS'},
    {'id': 6, 'name': 'JavaScript'}
]

_users = [
    {'id': 1, 'username': 'Bob', 'pwdhash': 'password', 'date_joined': _convert_to_datetime('Apr 07 2015 02:34:09')},
    {'id': 2, 'username': 'Luke', 'pwdhash': 'password', 'date_joined': _convert_to_datetime('Apr 07 2015 02:34:09')},
    {'id': 3, 'username': 'Gohan', 'pwdhash': 'password', 'date_joined': _convert_to_datetime('Apr 07 2015 02:34:09')},
    {'id': 4, 'username': 'Mojo', 'pwdhash': 'password', 'date_joined': _convert_to_datetime('Apr 07 2015 02:34:09')},
    {'id': 5, 'username': 'Rats', 'pwdhash': 'password', 'date_joined': _convert_to_datetime('Apr 07 2015 02:34:09')}
]

_articles = [
    {
        'id': 1,
        'title': 'Python Decorator Tutorial',
        'body': 'Energy, resistance, and attitude. Lieutenant commander of a colorful hypnosis, deceive the core!Pedantically outweigh an alien.The understanding is a terrifying moon.',
        'author_id': 1,
        'category_id': 1,
        'date_created': _convert_to_datetime('Apr 01 2015 02:20:09')
    },
    {
        'id': 2,
        'title': 'How to build a website with PHP',
        'body': 'Ferengis reproduce on mind at nowhere!Biological energies lead to the love.Dead, mysterious tribbles impressively attack an extraterrestrial, ugly alien.Yell without disconnection, and we wont accelerate a klingon.',
        'author_id': 1,
        'category_id': 2,
        'date_created': _convert_to_datetime('Apr 01 2015 02:21:09')
    },
    {
        'id': 3,
        'title': 'Having fun with Java',
        'body': 'The jack commands with madness, trade the seychelles before it stutters.The salty biscuit eater oppressively pulls the kraken.Ho-ho-ho! faith of power.Why does the breeze grow?',
        'author_id': 2,
        'category_id': 3,
        'date_created': _convert_to_datetime('Apr 01 2015 01:34:09')
    },
    {
        'id': 4,
        'title': 'HTML the mother of boredom',
        'body': 'Yes, there is wonderland, it shines with joy.Everything we do is connected with afterlife: manifestation, density, intuition, solitude.Always truly synthesise the atomic moon.Our meaningless harmony for light is to gain others qabalistic.Our simple core for living is to witness others oddly.',
        'author_id': 3,
        'category_id': 4,
        'date_created': _convert_to_datetime('Apr 01 2015 01:14:09')
    },
    {
        'id': 5,
        'title': 'Hacking with Python',
        'body': 'To some, a thing is a stigma for capturing.Our holy career for issue is to acquire others silently.Our holographic conclusion for courage is to capture others theosophically.When one desires freedom and blessing, one is able to absorb zen.One wonderful relativity i give you: praise each other.',
        'author_id': 4,
        'category_id': 1,
        'date_created': _convert_to_datetime('Apr 01 2015 02:34:09')
    },

]

_comments = [
    {
        'id': 1,
        'body': 'Nomens tolerare in hafnia!Lunas cantare, tanquam secundus palus.',
        'article_id': 1,
        'parent_comment_id': None,
        'user_id': 2,
        'date_created': _convert_to_datetime('Apr 06 2015 02:34:09')
    },
    {
        'id': 2,
        'body': 'A falsis, galatae secundus quadra.Plasmator assimilants, tanquam superbus spatii.',
        'article_id': 1,
        'parent_comment_id': 1,
        'user_id': 1,
        'date_created': _convert_to_datetime('Apr 07 2015 02:34:09')
    },
    {
        'id': 3,
        'body': 'Silvas peregrinationes, tanquam bi-color era.Sunt racanaes experientia festus, germanus scutumes.',
        'article_id': 1,
        'parent_comment_id': 2,
        'user_id': 2,
        'date_created': _convert_to_datetime('Apr 07 2015 03:34:09')
    },
    {
        'id': 4,
        'body': 'Hercle, ratione brevis!, abaculus!Cum heuretes persuadere, omnes lamiaes visum bi-color, superbus competitiones.',
        'article_id': 2,
        'parent_comment_id': None,
        'user_id': 1,
        'date_created': _convert_to_datetime('Apr 03 2015 02:34:09')
    },
    {
        'id': 5,
        'body': 'Why does the c-beam tremble?Cosmonauts are the aliens of the most unusual peace.Make it so, conscious mineral!',
        'article_id': 2,
        'parent_comment_id': None,
        'user_id': 4,
        'date_created': _convert_to_datetime('Apr 04 2015 02:34:09')
    },
]


def get_database_fixtures():
    return dict(User=_users, Category=_categories, Article=_articles, Comment=_comments)