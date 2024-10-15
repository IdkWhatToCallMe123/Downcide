import flet as ft
import yt_dlp
from yt_dlp.utils import download_range_func

adaptiveOnOff = False


class dlLogger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        #print(msg)
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)



def dlHook(d):
    try:
        if d['status'] == 'downloading' and 'total_bytes' in d:
            #print for debug
            '''
            print(int(round((int(d['downloaded_bytes']) / int(d['total_bytes'])) * 100, 0)), end="\r")
            print((int(d['downloaded_bytes']) / int(d['total_bytes'])))
            print(round((int(d['downloaded_bytes']) / int(d['total_bytes'])), 1))            
            '''

            downloadSheet.downloadProgressBar.value = round((int(d['downloaded_bytes']) / int(d['total_bytes'])), 5)
            downloadSheet.downloadProgressBar.update()
            
            downloadSheet.downloadProgressLabel.value = (str(round(int(d['downloaded_bytes'])/1000000, 1)) + " MB / " + str(round(int(d['total_bytes'])/1000000, 1)) + " MB")
            downloadSheet.downloadProgressLabel.update()
            
        elif d['status'] == 'downloading' and 'fragment_count' in d:
            #print for debug
            print(int(round((int(d['fragment_index']) / int(d['fragment_count'])) * 100, 2)), end="\r")       
            downloadSheet.downloadProgressBar.value = round((int(d['fragment_index']) / int(d['fragment_count'])), 5)
            downloadSheet.downloadProgressBar.update()
            
            if 'total_bytes_estimate' in d:
                dowloadedMegabytes = round(int(d['total_bytes_estimate']) * ((int(d['fragment_index']) / int(d['fragment_count']))) / 1000000, 1)
                totalMegabytes = round(int(d['total_bytes_estimate']) / 1000000, 1)
                
                downloadSheet.downloadProgressLabel.value = f"Approx. {dowloadedMegabytes}MB / {totalMegabytes}MB "
                downloadSheet.downloadProgressLabel.update()
            
            else:
                downloadSheet.downloadProgressLabel.value = f"Approx. {dowloadedMegabytes}MB / {totalMegabytes}M B"
                downloadSheet.downloadProgressLabel.update()
                
                 
    except Exception as e:
        raise Exception(e)
    
    if d['status'] == 'finished':
        print('Done downloading, now post-processing ...')
        
        downloadSheet.title.value = "Post-rocessing"
        downloadSheet.doneButton.disabled = False
        downloadSheet.bs.update()

#-----------

class downloadSheet:
    def resetBs():
        downloadSheet.title.value = "Downloading"
        downloadSheet.downloadProgressBar.value = None
        downloadSheet.downloadProgressLabel.value = "Preparing..."
        downloadSheet.doneButton.disabled = True
        downloadSheet.bs.open = False
        
        downloadSheet.bs.update()
    
    def closeBs():
        downloadSheet.bs.open = False
        downloadSheet.bs.update()
        
    title = ft.Text("Downloading", size=24)    
        
    downloadProgressBar = ft.ProgressBar(width=400)
    downloadProgressLabel = ft.Text("Preparing...")
    
    doneButton = ft.TextButton("Done", disabled=True, on_click=lambda _: downloadSheet.closeBs())
    
    bs = ft.BottomSheet(
        dismissible=False,
        content=ft.Container(
            padding=50,
            content=ft.Column(
                tight=True,
                controls=[
                    title,                 
                    downloadProgressBar,
                    downloadProgressLabel,
                     
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        tight=False,
                        width=400,
                        controls=[
                            doneButton
                            #ft.TextButton("Done", on_click=lambda _: page.close(bs)),
                        ]                        
                    ),
                    
                    
                ]
            )
        )
    )       

#--------


def main(page: ft.Page):    
    def downLoadButtonClicked(e):
        try:
            downloadSheet.resetBs()
            
        except AssertionError:
            pass
            # This happens when the thing isn't open
        
        try:            
            page.open(downloadSheet.bs)
            page.update()
            
            ydl_opts = {
                'logger': dlLogger(),
                'progress_hooks': [dlHook]
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(urlEntry.value, download=False)
                
                videoTitle = info_dict.get('title', None)
                videoChannel = info_dict.get('channel', None)
                videoTumbnail = info_dict.get('thumbnail', None)
                
                print(videoTitle)
                print(videoChannel)
                print(videoTumbnail)
                
                ydl.download(urlEntry.value)
                
        except Exception as e:
            downloadSheet.resetBs()
            
            
            if ("not a valid URL" in str(e)):
                #page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"))
                page.snack_bar = ft.SnackBar("Your URL appears to invalid")
                page.snack_bar.open = True
                page.update()
            else:
                print(e)
                errorMsgDialog.content=ft.Text(e, selectable=True)
                page.open(errorMsgDialog)
           
        
    #--------------
    
    def closeDialog(e):
        page.close(errorMsgDialog)  
        
        
    errorMsgDialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Error:"),
        content=ft.Text("Details"),
        actions=[
            ft.TextButton("Close", on_click=closeDialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    #==============================================
    # Here is the actuall main page
    

    urlEntry = ft.TextField(label="YouTube  URL", adaptive=adaptiveOnOff)

    page.add( 
        ft.Container(content=ft.Text("Downcide", size=32), padding=8),
        ft.Container(content=urlEntry, padding=8),
        ft.Container(
            content=ft.FilledButton(
                "Download", 
                icon="download", 
                adaptive=adaptiveOnOff,
                on_click=downLoadButtonClicked
                ),
            alignment=ft.alignment.center,
            padding=6,
        )        
    )


  
ft.app(main)