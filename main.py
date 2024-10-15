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

            downloadSheet.downloadProgressBar.value = round((int(d['downloaded_bytes']) / int(d['total_bytes'])), 5)
            downloadSheet.downloadProgressBar.update()
            
            downloadSheet.downloadProgressLabel.value = (str(round(int(d['downloaded_bytes'])/1000000, 1)) + " MB / " + str(round(int(d['total_bytes'])/1000000, 1)) + " MB")
            downloadSheet.downloadProgressLabel.update()
            
        elif d['status'] == 'downloading' and 'fragment_count' in d:
            #print for debug
            downloadSheet.downloadProgressBar.value = round((int(d['fragment_index']) / int(d['fragment_count'])), 5)
            downloadSheet.downloadProgressBar.update()
            
            if 'total_bytes_estimate' in d:
                # Explanation:
                # total bytes * (fragment index / fragment count)
                
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

def downloadVideo():
    url = mainPageControls.urlEntry.value
    
    mainPageControls.urlEntry.value = ""
    mainPageControls.urlEntry.update()
    
    confimationSheet.bs.open = False
    confimationSheet.bs.update()
    
    downloadSheet.bs.open = True
    downloadSheet.bs.update()
    
    ydl_opts = {
        'logger': dlLogger(),
        'progress_hooks': [dlHook]
    }
        
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
            
        ydl.download(url)
    

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

class confimationSheet:
    def resetBs():
        '''
        confimationSheet.title.value = "Downloading"
        confimationSheet.downloadProgressBar.value = None
        confimationSheet.downloadProgressLabel.value = "Preparing..."
        confimationSheet.doneButton.disabled = True
        confimationSheet.bs.open = False
        
        downloadSheet.bs.update()
        '''
        
    def openBs():
        confimationSheet.bs.open = True
        
        ydl_opts = {
            'logger': dlLogger(),
            'progress_hooks': [dlHook]
        }
        
        mainPageControls.spinner.visible = True
        mainPageControls.spinner.update()
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(mainPageControls.urlEntry.value, download=False)
                
            videoTumbnail = info_dict.get('thumbnail', None)
            videoTitle = info_dict.get('title', None)
            videoChannel = info_dict.get('channel', None)
            
            confimationSheet.Thumbnail.src = videoTumbnail
            confimationSheet.videoTitleText.value = videoTitle
            confimationSheet.videoChannelText.value = videoChannel 
            
            mainPageControls.spinner.visible = False
            mainPageControls.spinner.update()
        
        confimationSheet.bs.update()   
        
    
    def closeBs():
        confimationSheet.bs.open = False
        confimationSheet.bs.update()
        
       
    Thumbnail = ft.Image(
        # gets the youtube thumbnail,
            src="./generic_thumbnail.png",
            height=120,
            fit=ft.ImageFit.CONTAIN,
            repeat=ft.ImageRepeat.NO_REPEAT,
            border_radius=ft.border_radius.all(10),
        )
        
    videoTitleText = ft.Text("Title", size=24, width=340, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)    
    videoChannelText = ft.Text("Title", size=16, width=400, max_lines=1)    

    cancelButton = ft.OutlinedButton("Cancel", on_click=lambda _: confimationSheet.closeBs())
    downloadButton = ft.FilledButton("Download", icon="download", on_click=lambda _: downloadVideo()) #download video    
    
    bs = ft.BottomSheet(
        dismissible=True,
        enable_drag=True,
        show_drag_handle=False,
        content=ft.Container(
            padding=50,
            content=ft.Column(
                tight=True,
                spacing=38,
                controls=[
                    ft.Row(spacing=18,
                        controls=[
                            Thumbnail,                            
                            ft.Column(
                                controls=[
                                    videoTitleText,
                                    videoChannelText,
                                ]
                            ),
                        ]
                    ),           
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        tight=False,
                        controls=[
                            cancelButton,
                            downloadButton
                        ]                        
                    ),                 
                ]
            )
        )
    )
        
#----------------------

class mainPageControls:
    spinner = ft.ProgressRing(width=20, height=20, visible=False)
    urlEntry = ft.TextField(label="YouTube  URL", adaptive=adaptiveOnOff)


def main(page: ft.Page):    
    def downLoadButtonClicked(e):
        try:
            downloadSheet.resetBs()
            
        except AssertionError:
            pass
            # This happens when the thing isn't open
        
        try:            
            #page.open(confimationSheet.bs)
            
            #page.update()
            confimationSheet.openBs()
            
            ydl_opts = {
                'logger': dlLogger(),
                'progress_hooks': [dlHook]
            }

                
        except Exception as e:
            #downloadSheet.resetBs()            
            
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
    
    #-------------
    # I have to add this is the page for whatever reason
    page.add(downloadSheet.bs)
    page.add(confimationSheet.bs)
    
    #==============================================
    # Here is the actuall main page

    page.add( 
        ft.Container(content=ft.Text("Downcide", size=32), padding=8),
        ft.Container(content=mainPageControls.urlEntry, padding=8),
        
        ft.Container(
            alignment=ft.alignment.center,
            padding=6,
            
            content=ft.Row(
                tight=True,
                controls=[
                    ft.FilledButton(
                    "Download", 
                    icon="download", 
                    adaptive=adaptiveOnOff,
                    on_click=downLoadButtonClicked
                ),
                mainPageControls.spinner
                ]                
            )
        )        
    )

  
ft.app(
    main,
    assets_dir="icons"
    )