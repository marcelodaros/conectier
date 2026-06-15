import flet as ft
import asyncio
import core

async def main(page: ft.Page):
    page.title = "Conectier"
    page.window.icon = "icon.png"
    page.window.width = 850
    page.window.height = 550
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#121212"

    # Theme colors
    primary_color = "#00ADB5"
    surface_color = "#1E1E1E"
    text_color = "#EEEEEE"
    subtext_color = "#AAAAAA"
    error_color = "#FF4C4C"
    success_color = "#00D166"

    # Status Text
    status_text = ft.Text("Pronto para conectar.", size=13, color=subtext_color, italic=True)

    def set_status(msg, color=subtext_color):
        status_text.value = msg
        status_text.color = color
        page.update()

    # Left Column (Inputs)
    title = ft.Text("Conectier", size=36, weight=ft.FontWeight.W_800, color=primary_color)
    subtitle = ft.Text("Seus servidores a um clique", size=14, color=subtext_color)
    
    ip_input = ft.TextField(
        label="Endereço IP / Hostname", 
        prefix_icon=ft.Icons.DNS, 
        border_radius=8, 
        border_color="transparent", 
        bgcolor="#2A2A2A",
        height=55
    )
    user_input = ft.TextField(
        label="Usuário de Rede", 
        prefix_icon=ft.Icons.PERSON, 
        border_radius=8, 
        border_color="transparent", 
        bgcolor="#2A2A2A",
        height=55
    )
    pass_input = ft.TextField(
        label="Senha", 
        password=True, 
        can_reveal_password=True, 
        prefix_icon=ft.Icons.LOCK, 
        border_radius=8, 
        border_color="transparent", 
        bgcolor="#2A2A2A",
        height=55
    )

    btn_buscar = ft.Button(
        "BUSCAR COMPARTILHAMENTOS", 
        icon=ft.Icons.SEARCH, 
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE, 
            bgcolor=primary_color,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(20, 18, 20, 18)
        ),
        width=300
    )

    left_column = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    ft.Column([title, subtitle], spacing=0), 
                    margin=ft.Margin(bottom=30, left=0, right=0, top=0)
                ),
                ip_input,
                user_input,
                pass_input,
                ft.Container(btn_buscar, margin=ft.Margin(top=20, bottom=0, left=0, right=0))
            ],
            spacing=15
        ),
        padding=40,
        width=380,
        bgcolor=surface_color,
        border_radius=ft.BorderRadius(top_left=0, top_right=30, bottom_left=0, bottom_right=30),
    )

    # Right Column (List & Actions)
    shares_listview = ft.ListView(expand=True, spacing=5)
    checkboxes = []
    
    btn_mapear = ft.Button(
        "MAPEAR", 
        icon=ft.Icons.FOLDER_SHARED, 
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE, 
            bgcolor="#3A3F58",
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(0, 15, 0, 15)
        ),
        expand=True
    )
    
    btn_desconectar = ft.Button(
        "DESCONECTAR", 
        icon=ft.Icons.LINK_OFF, 
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE, 
            bgcolor=error_color,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(0, 15, 0, 15)
        ),
        expand=True
    )

    right_column = ft.Container(
        content=ft.Column(
            [
                ft.Text("Pastas Disponíveis", size=20, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Container(
                    content=shares_listview,
                    expand=True,
                    bgcolor="#1A1A1A",
                    border_radius=8,
                    padding=10,
                    margin=ft.Margin(top=10, bottom=15, left=0, right=0)
                ),
                ft.Row([btn_mapear, btn_desconectar], spacing=15),
                ft.Container(status_text, margin=ft.Margin(top=10, bottom=0, left=0, right=0))
            ]
        ),
        padding=40,
        expand=True
    )

    # Main Layout
    main_row = ft.Row(
        [left_column, right_column],
        expand=True,
        spacing=0
    )
    page.add(main_row)

    # Button logics
    async def btn_buscar_click(e):
        ip = ip_input.value.strip()
        login = user_input.value.strip()
        senha = pass_input.value.strip()

        if not ip or not login or not senha:
            set_status("Por favor, preencha todos os campos.", error_color)
            return

        set_status("Buscando pastas...", ft.Colors.AMBER_400)
        btn_buscar.disabled = True
        page.update()

        success, shares, error_msg = await asyncio.to_thread(core.list_workspaces, ip, login, senha)

        btn_buscar.disabled = False
        shares_listview.controls.clear()
        checkboxes.clear()

        if not success:
            set_status(error_msg, error_color)
        elif not shares:
            set_status("Nenhuma pasta encontrada.", ft.Colors.AMBER_400)
        else:
            for s in shares:
                cb = ft.Checkbox(label=s, value=False, fill_color=primary_color)
                checkboxes.append(cb)
                shares_listview.controls.append(cb)
            set_status(f"{len(shares)} pastas encontradas.", success_color)
        
        page.update()

    async def btn_mapear_click(e):
        selected_shares = [cb.label for cb in checkboxes if cb.value]
        
        if not selected_shares:
            set_status("Selecione pelo menos uma pasta.", error_color)
            return

        ip = ip_input.value.strip()
        login = user_input.value.strip()
        senha = pass_input.value.strip()

        set_status("Mapeando...", ft.Colors.AMBER_400)
        btn_mapear.disabled = True
        page.update()

        success_count, error_str = await asyncio.to_thread(core.mount_workspaces, ip, login, senha, selected_shares)

        btn_mapear.disabled = False
        if error_str:
            set_status(f"{success_count} mapeadas.\nErros:\n{error_str}", error_color)
        else:
            set_status(f"Sucesso! {success_count} pastas mapeadas.", success_color)
        page.update()

    async def btn_desconectar_click(e):
        def close_dlg(e):
            confirm_dialog.open = False
            page.update()

        async def confirm_disconnect(e):
            confirm_dialog.open = False
            set_status("Desconectando...", ft.Colors.AMBER_400)
            btn_desconectar.disabled = True
            page.update()

            success, msg = await asyncio.to_thread(core.disconnect_all)

            btn_desconectar.disabled = False
            if success:
                set_status(msg, success_color)
            else:
                set_status(f"Erro: {msg}", error_color)
            page.update()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Atenção", color=error_color),
            content=ft.Text("Desconectar TODAS as unidades de rede?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.TextButton("Desconectar", on_click=confirm_disconnect, style=ft.ButtonStyle(color=error_color)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        page.update()

    btn_buscar.on_click = btn_buscar_click
    btn_mapear.on_click = btn_mapear_click
    btn_desconectar.on_click = btn_desconectar_click

if __name__ == "__main__":
    ft.run(main, assets_dir=".")
