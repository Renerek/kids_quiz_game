#!/usr/bin/env python
"""
Render a Django template and print output.
Usage:
  python scripts/render_template.py quiz/emails/verification_email.html '{"display_name":"Test","verify_url":"https://ex/1","contact_url":"https://ex/contact"}'
"""
import sys
import json
import django

# Ensure the Django settings are configured by importing manage
# We'll use the project's manage.py to set DJANGO_SETTINGS_MODULE when running via manage.py shell or ensure the environment is correct.

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: render_template.py <template_path> '<context_json>'")
        sys.exit(2)
    template = sys.argv[1]
    ctx_json = sys.argv[2]
    try:
        context = json.loads(ctx_json)
    except Exception as e:
        print(f"Failed to parse context JSON: {e}")
        sys.exit(2)
    # Setup Django
    try:
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mathquiz.settings')
        django.setup()
    except Exception as e:
        print(f"Failed to setup Django: {e}")
        sys.exit(1)
    from django.template.loader import render_to_string
    out = render_to_string(template, context)
    print(out)
