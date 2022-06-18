import pytest, logging, threading
from api.lib.api import stub_stockfish, with_stockfish, with_stockfish_nonblock
from time import sleep

logger = logging.getLogger(__name__)


@pytest.fixture()
def pre():
    stub_stockfish()
    return None


# test to make sure 2 instances cannot be using stockfish at the same time


def test_locking(pre):
    t = threading.Thread(target=child)

    t.start()
    sleep(1.0)
    with_stockfish_nonblock(is_none)
    t.join()
    with_stockfish_nonblock(is_not_none)


def child():
    logger.info("Grabbing Resource")
    with_stockfish(lambda stockfish: sleep(3.0))
    logger.info("Unlocked Resource")


def is_not_none(stockfish):
    try:
        assert stockfish != None
    except:
        logger.error("Stockfish is None")


def is_none(stockfish):
    try:
        assert stockfish == None
    except:
        logger.error("Stockfish is Not None")
