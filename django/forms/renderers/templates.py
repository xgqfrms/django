import os

from django import forms
from django.template import TemplateDoesNotExist
from django.template.backends.django import DjangoTemplates
from django.template.loader import get_template
from django.utils._os import upath
from django.utils.functional import cached_property

try:
    import jinja2
except ImportError:
    jinja2 = None

ROOT = upath(os.path.dirname(forms.__file__))


class StandaloneTemplateRenderer(object):
    """Render using only the built-in templates."""
    def get_template(self, template_name):
        return self.standalone_engine.get_template(template_name)

    def render(self, template_name, context, request=None):
        template = self.get_template(template_name)
        return template.render(context, request=request).strip()

    @cached_property
    def standalone_engine(self):
        if jinja2:
            from django.template.backends.jinja2 import Jinja2
            return Jinja2({
                'APP_DIRS': False,
                'DIRS': [os.path.join(ROOT, 'jinja2')],
                'NAME': 'djangoforms',
                'OPTIONS': {},
            })
        return DjangoTemplates({
            'APP_DIRS': False,
            'DIRS': [os.path.join(ROOT, 'templates')],
            'NAME': 'djangoforms',
            'OPTIONS': {},
        })


class TemplateRenderer(StandaloneTemplateRenderer):
    """Render first via TEMPLATES, then fall back to built-in templates."""
    def get_template(self, template_name):
        try:
            return get_template(template_name)
        except TemplateDoesNotExist as e:
            try:
                return super(TemplateRenderer, self).get_template(template_name)
            except TemplateDoesNotExist as e2:
                e.chain.append(e2)
            raise TemplateDoesNotExist(template_name, chain=e.chain)
