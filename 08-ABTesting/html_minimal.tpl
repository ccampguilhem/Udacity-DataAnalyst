{% extends 'full.tpl'%}
{%- block any_cell -%}
{%- if 'hide_export' in cell['metadata'].get('tags', []) -%}
    {{ '' }}
{% else %}
    {{ super() }}
{% endif %}
{% endblock any_cell %}
