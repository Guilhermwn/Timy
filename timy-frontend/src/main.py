import ast
import datetime

import flet as ft
import requests

BACKEND = "http://127.0.0.1:8000"


class Timy(ft.Container):
    def __init__(self):
        super().__init__()

        HEAD_OPTIONS = {
            "saida_casa": "Saída de Casa",
            "chegada_DIA1": "1º Chegada no DIA",
            "saida_DIA1": "1º Saída do DIA",
            "chegada_ufs": "Chegada na UFS",
            "saida_ufs": "Saída da UFS",
            "chegada_DIA2": "2º Chegada no DIA",
            "saida_DIA2": "2º Saída do DIA",
            "chegada_casa": "Chegada em Casa",
        }

        inputChooser = ft.Dropdown(
            label="Entrada",
            expand=True,
            options=[
                ft.DropdownOption(key=k, content=ft.Text(v), text=v)
                for k, v in HEAD_OPTIONS.items()
            ],
        )

        def date_handler(input: ft.TextField, data: str):
            date_info = datetime.datetime.fromisoformat(data)
            date_info = f"{date_info.year}-{date_info.month}-{date_info.day}"
            input.value = date_info
            input.page.update()

        dateInput = ft.TextField(
            label="Data",
            on_click=lambda e: self.page.open(
                ft.DatePicker(
                    on_change=lambda e: date_handler(dateInput, e.data),
                )
            ),
        )

        def time_handler(input: ft.TimePicker, data: str):
            time_info = datetime.datetime.strptime(data, "%H:%M").time()
            input.value = time_info
            input.page.update()

        timeInput = ft.TextField(
            label="Horário",
            on_click=lambda e: self.page.open(
                ft.TimePicker(on_change=lambda e: time_handler(timeInput, e.data))
            ),
        )

        def send_handler(e: ft.ControlEvent, option: str, date: str, time: str):
            if any(not x for x in [option, date, time]):
                e.page.open(ft.SnackBar(ft.Text("Campo vazio"), bgcolor=ft.Colors.RED))
            else:
                json = {"data": date, f"{option}": f"{time}"}
                try:
                    response = requests.post(f"{BACKEND}/add", json=json)
                    if response.status_code == 200:
                        response_text = ast.literal_eval(response.text)
                        e.page.open(
                            ft.SnackBar(
                                ft.Text(
                                    f"'{option}' de {date} foi {response_text['activity']}"
                                ),
                                bgcolor=ft.Colors.GREEN
                                if response_text["activity"] == "Adicionado"
                                else ft.Colors.ORANGE,
                            )
                        )
                except Exception as err:
                    e.page.open(
                        ft.SnackBar(ft.Text(f"Erro: {err}"), bgcolor=ft.Colors.RED)
                    )

        confirmButton = ft.ElevatedButton(
            "Enviar",
            on_click=lambda e: send_handler(
                e, inputChooser.value, dateInput.value, timeInput.value
            ),
        )

        def clear_inputs_handler(e, *args):
            for i in args:
                i.value = None
            e.page.update()

        clearButton = ft.ElevatedButton(
            "Limpar",
            on_click=lambda e: clear_inputs_handler(e, dateInput, timeInput),
        )
        
        mainLayout = ft.Column(
            controls=[
                inputChooser,
                dateInput,
                timeInput,
                ft.Row(
                    controls=[clearButton, confirmButton],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

        self.content = mainLayout
        self.padding = ft.Padding(left=20, right=20, top=40, bottom=30)

    def did_mount(self):
        try:
            ping = requests.get(f"{BACKEND}/ping", timeout=2)
            if ping.status_code == 200:
                self.page.open(
                    ft.SnackBar(
                        ft.Text("Conectado"), bgcolor=ft.Colors.BLUE, duration=5000
                    )
                )
        except Exception as err:
            self.page.open(
                ft.SnackBar(
                    ft.Text(f"Erro ao conectar: {err}"),
                    bgcolor=ft.Colors.RED_600,
                    duration=5000,
                )
            )


def main(page: ft.Page):
    page.title = "Timy"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    def check_connection(page):
        try:
            ping = requests.get(f"{BACKEND}/ping", timeout=2)
            if ping.status_code == 200:
                page.open(
                    ft.SnackBar(
                        ft.Text("Conectado"), bgcolor=ft.Colors.BLUE, duration=5000
                    )
                )
        except Exception as err:
            page.open(
                ft.SnackBar(
                    ft.Text(f"Erro ao conectar: {err}"),
                    bgcolor=ft.Colors.RED_600,
                    duration=5000,
                )
            )
    page.floating_action_button = page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.WIFI, on_click=lambda e:check_connection(page)
    )
    app = Timy()
    page.add(app)


ft.app(main)
