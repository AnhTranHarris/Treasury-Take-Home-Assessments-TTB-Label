import runpy
import sys
import types


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

    def popover(self, label, **kwargs):
        self.calls.append(("popover", label))
        return self

    def file_uploader(self, *args, **kwargs):
        self.calls.append(("file_uploader", args[0]))
        return None

    def camera_input(self, *args, **kwargs):
        self.calls.append(("camera_input", args[0]))
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
    assert "radio" in called
    assert "columns" in called
    assert "file_uploader" in called
    assert "popover" in called
    assert any(name == "popover" and value == "Take a photo" for name, value in fake.calls)
    assert "camera_input" in called
    assert "info" in called
