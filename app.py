from dash import Dash, html, dcc, Input, Output, State, callback, page_container, page_registry, no_update
from flask_caching import Cache

import dash_bootstrap_components as dbc
import jwt
import time
from apscheduler.schedulers.background import BackgroundScheduler

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

CACHE_CONFIG = {
    'CACHE_TYPE': 'FileSystemCache',
    "CACHE_DIR": './Cache'
}

cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

def get_departments_cache():
    departments = "zero_department"
    time.sleep(5)
    cache.set("latest_cache", departments)

def update_cache():
    old_data = cache.get("latest_cache")
    if old_data:
        cache.set("backup_data", old_data)
        cache.set("latest_data", get_departments_cache())
    else:
        get_departments_cache()

scheduler = BackgroundScheduler()
job = scheduler.add_job(update_cache, 'interval', minutes=30)
scheduler.start()


#todo как обащаться к отдельны м элементам
def get_auth_form():
    login_input = html.Div(
        [
            dbc.Label("Логин", html_for="login_input"),
            dbc.Input(type="text", id="login_input", placeholder="Введите логин"),
            dbc.FormText("", id="loginFormText", color="secondary")
        ],
        className="mb-3"
    )

    password_input = html.Div(
        [
            dbc.Label("Пароль", html_for="password_input"),
            dbc.Input(type="password", id="password_input", placeholder="Введите пароль"),
            dbc.FormText("", id="passwordFormText", color="secondary"),
            dcc.Checklist(
                id='show-password-checkbox',
                options=[{'label': 'Показать пароль', 'value': 'show'}],
                style={'display': 'inline-block', 'marginTop': '10px'}
            )
        ],
        className="mb-3"
    )

    form_button = dbc.Button("Войти", color="danger", id="auth_button")

    auth_form = [html.Div([login_input, password_input, form_button,],
                         style={"position": "fixed", "background-color": "rgba(255, 255, 255, 0.9)",
                                "height": "50vh", "width": "40vw", "top": "25vh", "left": "30vw", "border-radius": "6px",
                                "padding": "2%"}),
                html.Img(src="assets/field.jpg", style={"background-size": "cover",
                                                        "background-repeat": "no-repeat",
                                                        "background-position": "center",
                                                        "margin": "0",
                                                        "z-index": "-1",
                                                        "height": "100vh",
                                                        "width": "100vw",
                                                        "position": "absolute"
                                                        })]

    # auth = html.Div(
    #     [
    #         html.Img(src="assets/field.jpg", style={"background-size": "cover",
    #                                             "background-repeat": "no-repeat",
    #                                             "background-position": "center",
    #                                             "margin": "0",
    #                                             "z-index": "-1",
    #                                             "height": "100vh",
    #                                             "width": "100vh",
    #                                             "position": "absolute"
    #                                                 }),
    #         dcc.Input(id="log", placeholder="Логин"),
    #         dcc.Input(id="pas", placeholder="Пароль"),
    #         html.Button("Войти", id="auth", n_clicks=0),
    #         dcc.Input(id="out", placeholder="out"),
    #     ],
    #     id='auth_form'
    # )

    return auth_form

def get_main_form():
    h1 = html.H1("MAIN PAGE", id="h1")
    # links = [dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
    #             for page in page_registry.values()]
    links = dbc.Nav(
        [
         dbc.NavLink([html.Div(page["name"])], href=page["path"])
         for page in page_registry.values()
    ],
    vertical=True,
    pills=False
)
    main = links
    return [h1, main, page_container]

#todo сделать форму и подключиьь стили
#todo сделать динамический layout через функцию

app.layout = [
        html.Div(
            children=get_auth_form(),
            id="main"
        ),
        dcc.Store(id="client_store", storage_type="local"),
]

@callback(
    Output("main", "children"),
    Output("login_input", "className"),
    Output("loginFormText", "children"),
    Output("loginFormText", "className"),
    Output("password_input", "className"),
    Output("passwordFormText", "children"),
    Output("passwordFormText", "className"),
    Output("client_store", "data"),
    Input("auth_button", "n_clicks"),
    State("login_input", "value"),
    State("password_input", "value"),
    State("client_store", "data"),
)
def credentials(n_clicks, log, pas, store):
    try:
        departments = cache.get("latest_cache")
        if departments is None:
            raise ValueError
    except ValueError:
        departments = cache.get("backup_cache")
    print(departments)
    print(log, pas)
    # input вернет None если не будет ввода
    # res = request.cookies.get("session_token")
    if store:
        token = jwt.decode(store, key="secret", algorithms="HS256")
        print(token)
        return get_main_form(), no_update, no_update, no_update, no_update, no_update, no_update, no_update
    else:
        if log and pas:
            # делать функцию читающую логин и пароли из бд
            if log == "admin" and pas == "admin":
                token = jwt.encode({'log': log}, key="secret", algorithm="HS256")
                return get_main_form(), no_update, no_update, no_update, no_update, no_update, no_update, token
            elif log != "admin" and pas == "admin":
                return (no_update, "is-invalid", "Пользователь с таким логином не найден!", "text-danger",
                    no_update, no_update, no_update, no_update)
            elif log == "admin" and pas != "admin":
                return (no_update, no_update, no_update, no_update,
                        "is-invalid", "Неверный пароль!", "text-danger", no_update)
        elif not log and pas:
            return (no_update, "is-invalid", "Необходимо ввести логин!", "text-danger",
                    no_update, no_update, no_update, no_update)
        elif log and not pas:
            return (no_update, no_update, no_update, no_update,
                    "is-invalid", "Необходимо ввести пароль!", "text-danger", no_update)
        else:
            return no_update

@callback(
    Output("password_input", "type"),
    Input("show-password-checkbox", "value")
)
def turn_password_checkbox(value):
    if value and "show" in value:
        return "text"
    else:
        return "password"

if __name__ == "__main__":
    get_departments_cache()
    app.run(debug=False)
