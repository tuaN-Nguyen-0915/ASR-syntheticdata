from meddies.slugify import slugify_disease


def test_strips_vietnamese_diacritics_and_spaces():
    assert slugify_disease("Bong gân cổ chân") == "bong_gan_co_chan"


def test_lowercases_and_replaces_punctuation():
    assert slugify_disease("COVID-19") == "covid_19"


def test_none_returns_unknown_disease():
    assert slugify_disease(None) == "unknown_disease"


def test_empty_string_returns_unknown_disease():
    assert slugify_disease("") == "unknown_disease"


def test_whitespace_only_returns_unknown_disease():
    assert slugify_disease("   ") == "unknown_disease"


def test_symbols_only_returns_unknown_disease():
    assert slugify_disease("!!!") == "unknown_disease"
