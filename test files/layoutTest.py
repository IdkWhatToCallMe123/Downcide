import flet as ft

def main(page: ft.page):
    
    text = ft.Text("yehsss")
    
    button = ft.TextButton("hejllo", width=100, height=100)
    
    page.add(ft.Stack(
        controls=[
        button,
        ft.Container(content=text, 
        ),       
    ]))
    
    
    page.update()

ft.app(main)