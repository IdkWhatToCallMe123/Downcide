import flet as ft
import yt_dlp
from yt_dlp.utils import download_range_func
import datetime

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
            
            videoDuration = info_dict.get('duration', None)
            videoDurationMinutes = str(datetime.timedelta(seconds=int(videoDuration)))
            
            # Lazy logic to remove the begining zeroes if the video is shorter than 10 minutes or 
            # 1 hour respectively
            if videoDurationMinutes[0:3] == "0:0":
                videoDurationMinutes = videoDurationMinutes[3:]
            
            elif videoDurationMinutes[0:2] == "0:":
                videoDurationMinutes = videoDurationMinutes[2:]
            
            
            confimationSheet.Thumbnail.src = videoTumbnail
            confimationSheet.videoTitleText.value = videoTitle
            confimationSheet.videoTitleText.tooltip = videoTitle
            confimationSheet.videoChannelText.value = videoChannel 
            confimationSheet.videoDurationText.value = videoDurationMinutes
            
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
    videoDurationText = ft.Text("Unknown")

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
                            ft.Stack(controls=[                                
                            Thumbnail,  
                            ft.Container(margin=8, padding=2, border_radius=4, alignment=ft.alignment.bottom_right, right=0, bottom=0, bgcolor="#cc000000",
                                         content=videoDurationText,
                                ),
                                ]),                          
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
    def resetUrlEntry(e):
        mainPageControls.urlEntry.error_text = None
        mainPageControls.urlEntry.update()
    
    # when the download button is clicked or if the user presses enter while in the URL entry
    def downlaodAction(e):
        if "youtube.com" in mainPageControls.urlEntry.value:          
            try:
                downloadSheet.resetBs()

            except AssertionError:
                pass
                # This happens when the thing isn't open

            try:          
                confimationSheet.openBs()

            except Exception as e:
                mainPageControls.errorMsgDialog.content=ft.Text(e, selectable=True)
                mainPageControls.errorMsgDialog.open = True
                mainPageControls.errorMsgDialog.update()
                
                mainPageControls.spinner.visible = False
                mainPageControls.spinner.update()                                    
            
        else:
            mainPageControls.urlEntry.error_text = "That is not a YouTube™ URL u stoopid"
            mainPageControls.urlEntry.update()
    

    def closeErrorMsgDialog(e):
        mainPageControls.errorMsgDialog.open = False  
        mainPageControls.errorMsgDialog.update()
     
    
    errorMsgDialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Error:"),
        content=ft.Text("Details"),
        actions=[
            ft.TextButton("Close", on_click=closeErrorMsgDialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    
    
    spinner = ft.ProgressRing(width=20, height=20, visible=False)
    urlEntry = ft.TextField(label="YouTube  URL", adaptive=adaptiveOnOff, on_change=resetUrlEntry, on_submit=downlaodAction) # todo: on submit


def main(page: ft.Page):  
    #-----------------
    # I have to add this is the page for whatever reason
    page.add(downloadSheet.bs)
    page.add(confimationSheet.bs)    
    page.add(mainPageControls.errorMsgDialog)
    
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
                    on_click=mainPageControls.downlaodAction
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