{% extends 'python.tpl'%}

## remove any cell with tag "hide_export"
{%- block any_cell -%}
{%- if 'hide_export' not in cell['metadata'].get('tags', []) -%}
    {{ super() }}
{%- endif -%}
{%- endblock any_cell -%}

## remove markdown cells
{%- block markdowncell -%}
{%- endblock markdowncell -%}

## remove input cells with tag "magic"
{%- block input -%}
{%- if 'magic' in cell['metadata'].get('tags', []) -%}
    {{ '' }}
{%- else -%}
    {{ super() }}
{%- endif -%}
{%- endblock input -%}

## change the appearance of execution count
{%- block in_prompt -%}
{%- endblock in_prompt -%}
