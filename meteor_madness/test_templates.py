import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meteor_madness.settings')
django.setup()

from django.template.loader import get_template
from django.template import TemplateDoesNotExist, TemplateSyntaxError

print("Testing Templates...")
print("=" * 50)

templates_to_test = [
    'simulation/simulator.html',
    'simulation/home.html',
    'simulation/asteroid_list.html',
]

for template_name in templates_to_test:
    try:
        template = get_template(template_name)
        print(f"✓ {template_name} - Valid")
    except TemplateDoesNotExist:
        print(f"⚠ {template_name} - Not found (may be expected)")
    except TemplateSyntaxError as e:
        print(f"✗ {template_name} - Syntax Error: {e}")
    except Exception as e:
        print(f"✗ {template_name} - Error: {e}")

print("=" * 50)
print("Template validation complete!")
