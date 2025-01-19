from dash import register_page, html

register_page(__name__, title="page1")

layout = html.H1("page1")