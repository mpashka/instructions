import contextlib
import importlib.machinery
import importlib.util
import io
import re
import stat
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
_loader = importlib.machinery.SourceFileLoader("render", str(REPO / "render"))
_spec = importlib.util.spec_from_loader("render", _loader)
render = importlib.util.module_from_spec(_spec)
_loader.exec_module(render)

SECRET = "s3cr3t-<&>-value"


def fake_vault(content):
    calls = []

    def view(path):
        calls.append(path)
        return yaml.safe_dump(content)
    return render.VaultReader(view), calls


class Sandbox(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.out = self.tmp / "out"
        self._repo = render.REPO
        self.write("proj/AGENTS.md", "")
        self.task = "proj/docs/requests/task"
        self.built = self.out / "proj" / "task"

    def tearDown(self):
        render.REPO = self._repo
        self._tmp.cleanup()

    def write(self, name, text):
        path = self.tmp / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def make_template(self, fields, text, file_name="instruction.md"):
        render.REPO = self.tmp / "templates"
        self.write("templates/demo/fields.yaml", yaml.safe_dump({"fields": fields}))
        self.write(f"templates/demo/{file_name}", text)

    def run_main(self, *argv, vault=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = render.main([*argv, "--out", str(self.out)], vault=vault)
        return code, stdout.getvalue(), stderr.getvalue()


class RealTemplates(Sandbox):
    def test_every_template_renders_from_its_examples(self):
        names = render.list_templates()
        self.assertIn("chatgpt-gpt-oauth-action", names)
        sections = {n: {f: d["example"] for f, d in
                        (render.load_yaml(REPO / n / "fields.yaml").get("fields") or {}).items()}
                    for n in names}
        values = self.write(f"{self.task}/values.yaml", yaml.safe_dump(sections, allow_unicode=True))
        render.render(values, [], self.out, fake_vault({})[0])
        for name in names:
            for path in self.built.glob(f"proj-task-{name}.*"):
                text = path.read_text(encoding="utf-8")
                self.assertFalse("{{" in text, f"{path}: остался плейсхолдер")
                self.assertFalse("template-note:begin" in text, f"{path}: осталась пометка шаблона")


class Links(unittest.TestCase):
    def test_html_links_open_in_a_new_window(self):
        for path in REPO.glob("*/instruction.html"):
            text = path.read_text(encoding="utf-8")
            for tag in re.findall(r"<a\b[^>]*>", text):
                self.assertIn('target="_blank"', tag, f"{path}: {tag}")
                self.assertIn('rel="noopener"', tag, f"{path}: {tag}")
            bare = re.findall(r'<span class="mono">(https://[^<{]*)</span>', text)
            self.assertEqual([], bare, f"{path}: адрес текстом, а не ссылкой")


class Rendering(Sandbox):
    def test_substitutes_vault_secret_without_printing_it(self):
        self.make_template({"client_id": {}, "client_secret": {}},
                           "<p>{{client_id}} / {{ client_secret }}</p>", "instruction.html")
        self.write("proj/docs/requests/vault/app.yml", "")
        values = self.write(f"{self.task}/values.yaml",
                            "demo:\n  client_id: my-client\n"
                            "  client_secret: {vault: ../vault/app.yml, key: vault_secret}\n")
        vault, calls = fake_vault({"vault_secret": SECRET})

        code, stdout, stderr = self.run_main(str(values), "demo", vault=vault)

        self.assertEqual(0, code, stderr)
        self.assertNotIn(SECRET, stdout + stderr)
        self.assertIn("client_secret (vault)", stdout)
        self.assertEqual([(self.tmp / "proj/docs/requests/vault/app.yml").resolve()], calls)
        rendered = self.out / "proj" / "task" / "proj-task-demo.html"
        self.assertEqual("<p>my-client / s3cr3t-&lt;&amp;&gt;-value</p>", rendered.read_text())
        self.assertEqual(0o600, stat.S_IMODE(rendered.stat().st_mode))
        self.assertEqual(0o700, stat.S_IMODE((self.out / "proj").stat().st_mode))
        self.assertEqual(0o700, stat.S_IMODE((self.out / "proj" / "task").stat().st_mode))
        self.assertEqual(0o700, stat.S_IMODE(self.out.stat().st_mode))
        self.assertTrue((self.out / "README.md").is_file())

    def test_markdown_is_not_escaped_and_template_note_is_dropped(self):
        self.make_template({"url": {}}, "<!-- template-note:begin -->\n> шаблон\n"
                                        "<!-- template-note:end -->\n# Открой {{url}}\n")
        values = self.write(f"{self.task}/values.yaml", "demo:\n  url: https://a.example/?x=1&y=2\n")

        render.render(values, ["demo"], self.out, fake_vault({})[0])

        self.assertEqual("# Открой https://a.example/?x=1&y=2\n",
                         (self.out / "proj/task/proj-task-demo.md").read_text())

    def test_rerender_replaces_previous_output(self):
        self.make_template({"a": {}}, "{{a}}")
        values = self.write(f"{self.task}/values.yaml", "demo:\n  a: old\n")
        render.render(values, ["demo"], self.out, fake_vault({})[0])
        values.write_text("demo:\n  a: new\n")

        render.render(values, ["demo"], self.out, fake_vault({})[0])

        self.assertEqual("new", (self.out / "proj/task/proj-task-demo.md").read_text())

    def test_task_outside_docs_requests_keeps_its_path(self):
        self.make_template({"a": {}}, "{{a}}")
        values = self.write("proj/life/trip/values.yaml", "demo:\n  a: 1\n")

        render.render(values, ["demo"], self.out, fake_vault({})[0])

        self.assertTrue((self.out / "proj/life/trip/proj-trip-demo.md").is_file())

    def test_values_outside_project_is_refused(self):
        self.make_template({"a": {}}, "{{a}}")
        (self.tmp / "proj/AGENTS.md").unlink()
        values = self.write("loose/values.yaml", "demo:\n  a: 1\n")
        with self.assertRaises(render.RenderError) as caught:
            render.render(values, ["demo"], self.out, fake_vault({})[0])
        self.assertIn("вне проекта", str(caught.exception))


class Errors(Sandbox):
    def assert_fails(self, values_text, *expected, names=("demo",), vault=None):
        values = self.write(f"{self.task}/values.yaml", values_text)
        with self.assertRaises(render.RenderError) as caught:
            render.render(values, list(names), self.out, vault or fake_vault({})[0])
        for part in expected:
            self.assertIn(part, str(caught.exception))
        self.assertFalse((self.out / "proj").exists())
        return str(caught.exception)

    def test_missing_field_names_field_and_file(self):
        self.make_template({"a": {}, "b": {}}, "{{a}} {{b}}")
        self.assert_fails("demo:\n  a: 1\n  b: ''\n", "не заполнены поля b", str(self.tmp / self.task / "values.yaml"))

    def test_unknown_field(self):
        self.make_template({"a": {}}, "{{a}}")
        self.assert_fails("demo:\n  a: 1\n  typo: 2\n", "неизвестные поля typo")

    def test_placeholder_not_declared_in_template(self):
        self.make_template({"a": {}}, "{{a}} {{b}}")
        self.assert_fails("demo:\n  a: 1\n", "не объявленные", "b")

    def test_missing_vault_key(self):
        self.make_template({"a": {}}, "{{a}}")
        self.write(f"{self.task}/app.yml", "")
        message = self.assert_fails("demo:\n  a: {vault: app.yml, key: absent}\n", "нет ключа absent",
                                    vault=fake_vault({"other": SECRET})[0])
        self.assertNotIn(SECRET, message)

    def test_unknown_template_section(self):
        self.make_template({"a": {}}, "{{a}}")
        self.assert_fails("other:\n  a: 1\n", "нет раздела demo")

    def test_main_reports_error_to_stderr(self):
        self.make_template({"a": {}}, "{{a}}")
        values = self.write(f"{self.task}/values.yaml", "demo: {}\n")
        code, _, stderr = self.run_main(str(values))
        self.assertEqual(1, code)
        self.assertIn("не заполнены поля a", stderr)


class Cleaning(Sandbox):
    def setUp(self):
        super().setUp()
        self.make_template({"a": {}}, "{{a}}")
        self.write("templates/other/fields.yaml", "fields: {}\n")
        self.write("templates/other/instruction.md", "x")
        self.values = self.write(f"{self.task}/values.yaml", f"demo:\n  a: {SECRET}\nother: {{}}\n")
        render.render(self.values, [], self.out, fake_vault({})[0])
        self.neighbour = self.write("proj/docs/requests/next/values.yaml", "other: {}\n")
        render.render(self.neighbour, [], self.out, fake_vault({})[0])

    def test_clean_removes_named_template_of_the_task(self):
        code, _, _ = self.run_main("--clean", str(self.values), "demo")

        self.assertEqual(0, code)
        self.assertEqual(["proj-task-other.md"], sorted(p.name for p in (self.out / "proj/task").iterdir()))

    def test_clean_without_names_removes_the_task_only(self):
        self.run_main("--clean", str(self.values))

        self.assertFalse((self.out / "proj/task").exists())
        self.assertTrue((self.out / "proj/next/proj-next-other.md").is_file())


if __name__ == "__main__":
    unittest.main()
