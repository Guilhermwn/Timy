import ast
import datetime

import flet as ft
import requests


class Timy(ft.Container):
    def __init__(self):
        super().__init__()

        self.backend_link = ""

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

        # DropdownM2 está obsoleto e vai ser substituido completamente
        # na versão 0.30.0 do Flet
        # Buscar se o problema de expand=True não funcionar no Dropdown já foi resolvido
        inputChooser = ft.DropdownM2(
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
                e.page.open(
                    ft.SnackBar(
                        ft.Text("Campo vazio", weight=ft.FontWeight.W_500),
                        bgcolor=ft.Colors.RED,
                    )
                )
            else:
                json = {"data": date, f"{option}": f"{time}"}
                try:
                    response = requests.post(f"{self.backend_link}/add", json=json)
                    if response.status_code == 200:
                        response_text = ast.literal_eval(response.text)
                        e.page.open(
                            ft.SnackBar(
                                ft.Text(
                                    f"'{option}' de {date} foi {response_text['activity']}",
                                    weight=ft.FontWeight.W_500,
                                ),
                                bgcolor=ft.Colors.GREEN
                                if response_text["activity"] == "added"
                                else ft.Colors.ORANGE,
                            )
                        )
                except Exception as err:
                    e.page.open(
                        ft.SnackBar(
                            ft.Text(
                                f"Erro: {err}",
                                weight=ft.FontWeight.W_500,
                            ),
                            bgcolor=ft.Colors.RED,
                        )
                    )

        confirmButton = ft.ElevatedButton(
            "Enviar",
            icon=ft.Icons.SEND,
            on_click=lambda e: send_handler(
                e, inputChooser.value, dateInput.value, timeInput.value
            ),
        )

        def clear_inputs_handler(e, *args):
            for i in args:
                i.value = None
            e.page.update()

        clearButton = ft.ElevatedButton(
            text="Limpar",
            icon=ft.Icons.DELETE,
            on_click=lambda e: clear_inputs_handler(e, dateInput, timeInput),
        )

        mainLayout = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[inputChooser],
                        expand=True,
                    ),
                ),
                dateInput,
                timeInput,
                ft.Row(
                    controls=[clearButton, confirmButton],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            expand=True,
        )

        self.content = mainLayout
        self.expand = True
        self.padding = ft.Padding(left=20, right=20, top=40, bottom=30)

    def did_mount(self):
        self.backend_link = self.page.client_storage.get("backend-link")
        try:
            ping = requests.get(f"{self.backend_link}/ping")
            if ping.status_code == 200:
                if ping.text.strip('"') == "pong":
                    self.page.open(
                        ft.SnackBar(
                            ft.Text("Conectado", weight=ft.FontWeight.W_500),
                            bgcolor=ft.Colors.BLUE,
                            duration=5000,
                        )
                    )
                else:
                    self.page.open(
                        ft.SnackBar(
                            ft.Text(
                                f"Backend inadequado, resposta da requisição: {ping.text}",
                                weight=ft.FontWeight.W_500,
                            ),
                            bgcolor=ft.Colors.RED,
                            duration=5000,
                        )
                    )
        except Exception as err:
            self.page.open(
                ft.SnackBar(
                    ft.Text(f"Erro ao conectar: {err}", weight=ft.FontWeight.W_500),
                    bgcolor=ft.Colors.RED_600,
                    duration=5000,
                )
            )


def check_connection(page: ft.Page):
    try:
        ping = requests.get(
            f"{page.client_storage.get('backend-link')}/ping", timeout=2
        )
        if ping.status_code == 200:
            page.open(
                ft.SnackBar(
                    ft.Text("Conectado", weight=ft.FontWeight.W_500),
                    bgcolor=ft.Colors.BLUE,
                    duration=5000,
                )
            )
    except Exception as err:
        page.open(
            ft.SnackBar(
                ft.Text(f"Erro ao conectar: {err}", weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.RED_600,
                duration=5000,
            )
        )


def main(page: ft.Page):
    page.title = "Timy"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.WIFI, on_click=lambda e: check_connection(page)
    )

    def backend_dialog_handler(link: str = None):
        if link:
            page.client_storage.set("backend-link", link)
            page.close(backendDialog)
            page.open(
                ft.SnackBar(
                    ft.Text("Backend salvo com sucesso", weight=ft.FontWeight.W_500),
                    bgcolor=ft.Colors.GREEN,
                )
            )
        else:
            page.open(
                ft.SnackBar(
                    ft.Text("Campo Vazio", weight=ft.FontWeight.W_500),
                    bgcolor=ft.Colors.RED,
                )
            )

    backendTextField = ft.TextField(
        label="Adicionar link", value=page.client_storage.get("backend-link")
    )

    backendDialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Adicionar Backend"),
        content=backendTextField,
        actions=[
            ft.TextButton("Não", on_click=lambda e: page.close(backendDialog)),
            ft.TextButton(
                "Adicionar",
                on_click=lambda e: backend_dialog_handler(backendTextField.value),
            ),
        ],
    )

    page.appbar = ft.AppBar(
        title=ft.Text("Timy", size=20, text_align="start"),
        actions=[
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    on_click=lambda e: page.open(backendDialog),
                ),
                padding=ft.Padding(left=20, top=0, right=10, bottom=0),
            )
        ],
    )
    app = Timy()
    page.add(app)


ft.app(main)
