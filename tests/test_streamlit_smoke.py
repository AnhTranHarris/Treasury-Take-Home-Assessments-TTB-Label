import runpy
import sys
import types
from types import SimpleNamespace

from src.extraction.intake import FieldDraft


class FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cache_resource(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def set_page_config(self, **kwargs):
        self.calls.append(("set_page_config", kwargs))

    def title(self, value):
        self.calls.append(("title", value))

    def caption(self, value):
        self.calls.append(("caption", value))

    def markdown(self, value, **kwargs):
        self.calls.append(("markdown", value))

    def radio(self, label, options, **kwargs):
        self.calls.append(("radio", label))
        return options[0]

    def info(self, value):
        self.calls.append(("info", value))

    def text_input(self, label, value="", **kwargs):
        self.calls.append(("text_input", label))
        return value

    def number_input(self, label, value=0.0, **kwargs):
        self.calls.append(("number_input", label))
        return value

    def checkbox(self, label, value=False, **kwargs):
        self.calls.append(("checkbox", label))
        return value

    def columns(self, spec, **kwargs):
        self.calls.append(("columns", spec))
        return [self for _ in spec]

    def selectbox(self, label, options, **kwargs):
        self.calls.append(("selectbox", label))
        return options[0]

    def file_uploader(self, *args, **kwargs):
        self.calls.append(("file_uploader", args[0]))
        return None

    def button(self, *args, **kwargs):
        self.calls.append(("button", args[0]))
        return False


fake = FakeStreamlit()
sys.modules["streamlit"] = fake


def test_streamlit_entrypoint_renders_initial_path_without_starting_ocr():
    namespace = runpy.run_path("streamlit_app.py", run_name="ttb_streamlit_smoke")
    namespace["main"]()
    called = [name for name, _ in fake.calls]
    assert "set_page_config" in called
    assert any(
        name == "markdown" and "--ttb-gold" in value
        for name, value in fake.calls
    )
    assert any(
        name == "markdown" and "Unofficial take-home prototype" in value
        for name, value in fake.calls
    )
    assert "radio" in called
    assert "columns" in called
    assert "selectbox" in called
    assert "file_uploader" in called
    assert "button" in called
    assert any(name == "button" and value == "Take a photo" for name, value in fake.calls)
    assert "info" in called



def test_uncertain_field_has_theme_independent_yellow_banner():
    namespace = runpy.run_path("streamlit_app.py", run_name="ttb_review_markup")
    fake.calls.clear()
    uncertain = FieldDraft("partial", 0.61, True, "Score < 0.90 & unclear")
    namespace["_review_marker"]("Brand name", uncertain)
    warnings = [value for name, value in fake.calls if name == "markdown"]
    assert len(warnings) == 1
    assert 'role="alert"' in warnings[0]
    assert "ttb-review-flag" in warnings[0]
    assert "#FFE58F" in warnings[0]
    assert "#202020" in warnings[0]
    assert "Score &lt; 0.90 &amp; unclear" in warnings[0]

    fake.calls.clear()
    clear = FieldDraft("clear", 0.99, False, "Clear evidence")
    namespace["_review_marker"]("Brand name", clear)
    assert not fake.calls


def test_only_uncertain_input_fields_get_yellow_override():
    namespace = runpy.run_path("streamlit_app.py", run_name="ttb_review_inputs")
    fake.calls.clear()
    good = FieldDraft("good", 0.99, False, "Clear evidence")
    flagged = FieldDraft("partial", 0.61, True, "Needs review")
    draft = SimpleNamespace(
        brand=flagged,
        class_type=good,
        alcohol_content=good,
        net_contents=good,
        name_address=good,
        imported=good,
        country_origin=good,
        government_warning=good,
        age_statement=good,
        color_disclosure=good,
        commodity_statement=good,
    )
    namespace["_highlight_review_fields"](draft)
    styles = [value for name, value in fake.calls if name == "markdown"]
    assert len(styles) == 1
    assert ".st-key-intake_brand" in styles[0]
    assert ".st-key-intake_class_type" not in styles[0]
    assert "#FFF1B2" in styles[0]
    assert "#202020" in styles[0]
    assert "!important" in styles[0]

    fake.calls.clear()
    draft.brand = good
    namespace["_highlight_review_fields"](draft)
    assert not fake.calls
