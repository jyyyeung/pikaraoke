"""Pinyin readings, so Chinese titles join the A-Z strip and its sort order.

Without this a Han character lights no slot on the bar, so a Chinese library
renders a strip that is entirely grey and cannot be jumped with, and every
Chinese title piles up after Z instead of sitting with its pronunciation.
Filing 稻香 under D and 重庆 under C gives those songs the same section and the
same ordering as Latin ones.
"""

from functools import lru_cache

# The bar key and the sort key both read pypinyin's phrase dictionary, and its
# longest phrase is shorter than this, so the first syllable is fixed by this
# prefix. Keeping it short also lets titles with a common opening share a cache
# entry.
_PHRASE_WINDOW = 8

_HAN_RANGES = (
    (0x3400, 0x4DBF),  # Extension A
    (0x4E00, 0x9FFF),  # Unified Ideographs
    (0xF900, 0xFAFF),  # Compatibility Ideographs
    (0x20000, 0x2FA1F),  # Extensions B-F and Compatibility Supplement
)


def _is_han(char: str) -> bool:
    code = ord(char)
    return any(start <= code <= end for start, end in _HAN_RANGES)


def alpha_key(raw: str) -> str | None:
    """A-Z strip key for a lowercase filename stem, or None when it has no slot.

    ASCII is settled without pypinyin, so a Latin-only library never loads it.
    Han is filed under its pinyin initial ahead of the digit test, because 一 is
    both a Chinese numeral and Unicode's idea of a number; a Chinese library
    files it under Y.
    """
    first = raw[:1]
    if not first:
        return None
    if first.isascii():
        if first.isalpha():
            return first
        return "numeric" if first.isnumeric() else None
    initial = pinyin_initial(raw[:_PHRASE_WINDOW])
    if initial:
        return initial
    return "numeric" if first.isnumeric() else None


@lru_cache(maxsize=4096)
def pinyin_initial(text: str) -> str | None:
    """Lowercase pinyin initial of `text`'s leading Han character, or None.

    Reads the same window and dictionary as han_to_pinyin, so a title's bar
    letter cannot disagree with where its sort key files it. pypinyin is
    imported inside because it spends a third of a second loading dictionaries,
    which a Latin-only library should not pay at startup.
    """
    if not text or not _is_han(text[0]):
        return None
    initial = han_to_pinyin(text[:_PHRASE_WINDOW])[:1]
    return initial if initial.isascii() and initial.isalpha() else None


@lru_cache(maxsize=8192)
def han_to_pinyin(text: str) -> str:
    """Replace every Han character in `text` with its pinyin, keeping the rest.

    The sort key's transliteration, so 稻香 sorts as "daoxiang" next to Latin
    titles rather than after Z. The whole string is read at once so polyphones
    resolve in phrase context. Text without Han characters comes back untouched,
    which is also what keeps pypinyin out of a Latin-only library's startup.
    """
    if not any(_is_han(char) for char in text):
        return text
    from pypinyin import lazy_pinyin

    return "".join(lazy_pinyin(text, errors="default"))
