{% extends 'full.tpl'%}
{%- block any_cell -%}
{%- if 'hide_export' in cell['metadata'].get('tags', []) -%}
    {{ '' }}
{% else %}
    {{ super() }}
{% endif %}
{% endblock any_cell %}

{%- block input_group -%}
{%- if 'hide_input' in cell['metadata'].get('tags', []) -%}
    {{ '' }}
{% else %}
    {{ super() }}
{% endif %}
{% endblock input_group %}

