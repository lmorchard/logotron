import pytest
import logging

from .bot import Bot
from .config import Config


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def bot(config):
    return Bot(config=config)


@pytest.fixture
def logger():
    return logging.getLogger("test")


def test_extract_program_source_1(bot, logger):
    content_html = """<p><span class="h-card"><a href="https://toot.lmorchard.com/@logotron" class="u-url mention">@<span>logotron</span></a></span> boop boop <a href="https://toot.lmorchard.com/tags/logo" class="mention hashtag" rel="tag">#<span>logo</span></a> to randomwalk<br />repeat 1000 [<br />setpencolor (random 1 15)<br />make &quot;r random 3<br />if :r = 0 [ fd 20 ]<br />if :r = 1 [ rt 90 fd 20 ]<br />if :r = 2 [ lt 90 fd 20 ]<br />wait 1<br />]<br />end<br />fullscreen<br />randomwalk<br />wait 120<br />bye</p>"""
    expected = """to randomwalk
repeat 1000 [
setpencolor (random 1 15)
make "r random 3
if :r = 0 [ fd 20 ]
if :r = 1 [ rt 90 fd 20 ]
if :r = 2 [ lt 90 fd 20 ]
wait 1
]
end
fullscreen
randomwalk
wait 120
bye"""
    result = bot.extract_program_source(content_html)
    assert expected == result


def test_extract_program_source_2(bot, logger):
    content_html = """<p><span class="h-card"><a href="https://toot.lmorchard.com/@logotron" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank">@<span>logotron</span></a></span></p><p>random comment</p><p><a href="https://gts.decafbad.com/tags/logo" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>logo</span></a></p><p>to randomwalk<br>repeat 1000 [<br>setpencolor (random 1 15)<br>make "r random 3<br>if :r = 0 [ fd 20 ]<br>if :r = 1 [ rt 90 fd 20 ]<br>if :r = 2 [ lt 90 fd 20 ]<br>wait 1<br>]<br>end</p><p>fullscreen<br>randomwalk</p><p>wait 120<br>bye</p>"""
    expected = """to randomwalk
repeat 1000 [
setpencolor (random 1 15)
make "r random 3
if :r = 0 [ fd 20 ]
if :r = 1 [ rt 90 fd 20 ]
if :r = 2 [ lt 90 fd 20 ]
wait 1
]
end

fullscreen
randomwalk

wait 120
bye"""
    result = bot.extract_program_source(content_html)
    assert expected == result
