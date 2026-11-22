"""Tests for the pinyin readings behind the A-Z strip and the sort order."""

from pikaraoke.lib.pinyin import alpha_key, han_to_pinyin, pinyin_initial


class TestPinyinInitial:
    def test_simplified_title(self):
        assert pinyin_initial("稻香") == "d"

    def test_traditional_title(self):
        assert pinyin_initial("周杰倫") == "z"

    def test_polyphone_read_in_phrase_context(self):
        """重庆 is Chongqing, so the first syllable is C, not 重's default Z."""
        assert pinyin_initial("重庆森林") == "c"

    def test_lone_polyphone_uses_its_default_reading(self):
        assert pinyin_initial("重") == "z"

    def test_non_han_text_has_no_pinyin_initial(self):
        assert pinyin_initial("Abba - Waterloo") is None

    def test_empty_text(self):
        assert pinyin_initial("") is None

    def test_punctuation_before_han_has_no_initial(self):
        """The bar keys on the filename's first character, whatever it is."""
        assert pinyin_initial("《稻香》") is None


class TestHanToPinyin:
    def test_replaces_han_with_pinyin(self):
        assert han_to_pinyin("稻香") == "daoxiang"

    def test_polyphone_read_in_phrase_context(self):
        assert han_to_pinyin("重庆森林") == "chongqingsenlin"

    def test_mixed_text_keeps_latin_and_punctuation(self):
        assert han_to_pinyin("周杰伦 - 稻香") == "zhoujielun - daoxiang"

    def test_text_without_han_is_untouched(self):
        assert han_to_pinyin("99 Luftballons - Abba") == "99 Luftballons - Abba"


class TestAlphaKey:
    def test_latin_initial(self):
        assert alpha_key("abba - waterloo") == "a"

    def test_digit_groups_as_numeric(self):
        assert alpha_key("99 luftballons") == "numeric"

    def test_han_initial(self):
        assert alpha_key("稻香") == "d"

    def test_chinese_numeral_files_as_han(self):
        assert alpha_key("一生所爱") == "y"

    def test_fullwidth_digit_groups_as_numeric(self):
        assert alpha_key("１２３") == "numeric"

    def test_punctuation_has_no_slot(self):
        assert alpha_key("(i can't get no) satisfaction") is None

    def test_empty_has_no_slot(self):
        assert alpha_key("") is None

    def test_bar_key_agrees_with_the_sort_key(self):
        """The windowed and full-string readers must agree on the first syllable."""
        for title in ("稻香", "重庆森林", "周杰倫", "一生所爱", "A-Lin - 给我一个理由忘记"):
            assert alpha_key(title) == han_to_pinyin(title)[:1]
