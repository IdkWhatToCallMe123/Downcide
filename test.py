import yt_dlp

#URLS = ['https://www.youtube.com/watch?v=lxMWSmKieuc'] #long vid
URLS = ['https://www.youtube.com/watch?v=rnzaiYrvvrw'] #short vid

class MyLogger:
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


# ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
def my_hook(d):
    
    try:
        if d['status'] == 'downloading' and 'total_bytes' in d:
            print(int(round((int(d['downloaded_bytes']) / int(d['total_bytes'])) * 100, 2)), end="\r")
        
        elif d['status'] == 'downloading' and 'fragment_count' in d:
            print(int(round((int(d['fragment_index']) / int(d['fragment_count'])) * 100, 2)), end="\r")
            
            
    except Exception as e:
        raise Exception(e)
    
    if d['status'] == 'finished':
        print('Done downloading, now post-processing ...')


ydl_opts = {
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(URLS)