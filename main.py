import flet as ft

adaptiveOnOff = False

def main(page: ft.Page):


    urlEntry = ft.TextField(label="Spotify song URL", adaptive=adaptiveOnOff)

    page.add( 
        ft.Container(content=ft.Text("Downcide", size=32), padding=8),
        ft.Container(content=urlEntry, padding=8),
        ft.Container(
            content=ft.FilledButton("Download", icon="download", adaptive=adaptiveOnOff),
            alignment=ft.alignment.center,
            padding=6
        )        
        )


ft.app(main)