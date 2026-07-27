from meddies.think_strip import strip_think_block


def test_strips_closed_think_block():
    content = "<think> internal reasoning here </think> Hello, how can I help?"
    cleaned, warning = strip_think_block(content)
    assert cleaned == "Hello, how can I help?"
    assert warning is None


def test_passes_through_content_without_think_tag():
    content = "Hello, how can I help?"
    cleaned, warning = strip_think_block(content)
    assert cleaned == "Hello, how can I help?"
    assert warning is None


def test_unclosed_think_tag_returns_original_with_warning():
    content = "<think> reasoning that never closes... still going"
    cleaned, warning = strip_think_block(content)
    assert cleaned == content
    assert warning == "unclosed think tag"


def test_strips_only_first_think_block_and_trims_whitespace():
    content = "<think>plan</think>   Reply text here.  "
    cleaned, warning = strip_think_block(content)
    assert cleaned == "Reply text here."
    assert warning is None
