from bot.lib.utils import is_elo

def test_is_elo():
    assert is_elo('12345678') == True
    assert is_elo('EmmaIsCool') == False
    assert is_elo('11') == True
    assert is_elo('Tr1sta0') == False
