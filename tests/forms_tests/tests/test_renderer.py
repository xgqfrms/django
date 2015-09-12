import os
import unittest

from django.forms.renderers.templates import (
    ROOT, StandaloneTemplateRenderer, TemplateRenderer,
)
from django.template import TemplateDoesNotExist
from django.test import SimpleTestCase
from django.utils._os import upath

try:
    import jinja2
except ImportError:
    jinja2 = None


class StandaloneTemplateRendererTests(SimpleTestCase):
    tpl_name = 'django/forms/widgets/input.html'

    @unittest.skipUnless(jinja2, 'jinja2 not installed.')
    def test_get_template_jinja2(self):
        renderer = StandaloneTemplateRenderer()
        tpl = renderer.get_template(self.tpl_name)
        expected_path = os.path.join(ROOT, 'jinja2', self.tpl_name)
        self.assertEqual(upath(tpl.origin.name), expected_path.replace('/', os.sep))

    @unittest.skipIf(jinja2, 'jinja2 installed.')
    def test_get_template_dtl(self):
        renderer = StandaloneTemplateRenderer()
        tpl = renderer.get_template(self.tpl_name)
        expected_path = os.path.join(ROOT, 'templates', self.tpl_name)
        self.assertEqual(tpl.origin.name, expected_path)

    def test_render(self):
        """Uses given context to render template."""
        renderer = StandaloneTemplateRenderer()
        html = renderer.render(self.tpl_name, {'widget': {'attrs': {}, 'type': 'foo'}})
        self.assertIn('type="foo"', html)


class TemplateRendererTests(SimpleTestCase):
    def test_custom_template_found(self):
        """Can find a custom template via TEMPLATES config."""
        renderer = TemplateRenderer()
        # Found because forms_tests is in INSTALLED_APPS.
        tpl = renderer.get_template('forms_tests/custom_widget.html')
        expected_path = os.path.abspath(
            os.path.join(
                upath(os.path.dirname(__file__)),
                '..',
                'templates/forms_tests/custom_widget.html',
            )
        )
        self.assertEqual(tpl.origin.name, expected_path)

    def test_fallback_to_builtin_template(self):
        renderer = TemplateRenderer()
        tpl = renderer.get_template('django/forms/widgets/input.html')
        # Sufficiently generic to pass for either DTL or Jinja2.
        self.assertTrue(tpl.origin.name.startswith(ROOT))

    def test_template_not_found(self):
        renderer = TemplateRenderer()
        with self.assertRaises(TemplateDoesNotExist) as cm:
            renderer.get_template('does/not/exist.html')
        # Records that both TEMPLATES engine and standalone engine were tried.
        self.assertEqual(len(cm.exception.chain), 2)
