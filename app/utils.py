import time
from subprocess import Popen, PIPE, TimeoutExpired

def mediaconverter(filename, format, video=False):
    encoders = {"mp3": "lamemp3enc", "wav": "wavenc", "aac": "avenc_aac", "ogg": "vorbisenc"}
    input_path, output_path = f'./app/uploads/{filename}', f"./app/converted/{''.join(filename.split('.')[0:-1])}.{format}"

    bash_script = []

    if video:
       if filename.split('.')[-1] == 'ts':
           bash_script = ['gst-launch-1.0', 'qtmux', 'name=mx', '!', 'filesink', f'location={output_path}', 'sync=false', 'filesrc', f'location={input_path}', '!', 'tsdemux', 'name=dmx', 'dmx.', '!', 'queue', '!', 'h264parse', '!', 'mx.', 'dmx.', '!', 'queue', '!', 'aacparse', '!', 'faad', '!', 'audioresample', '!', 'audioconvert', '!', 'voaacenc', '!', 'mx.']

    else:    
        bash_script = ['gst-launch-1.0', 'filesrc', f'location={input_path}', '!',  'decodebin', '!', 'audioconvert', '!', f'{encoders[format]}', '!', 'filesink', f'location={output_path}']
        
    if bash_script:
        
        transcode_proc = Popen(bash_script)

        if transcode_proc.poll() is None:
            time.sleep(10)
        
        return f"{''.join(filename.split('.')[0:-1])}.{format}"
    else:
        return ''




#gst-luanch-1.0 filesrc location=f"{input_path}" ! decodebin name=dbin dbin. ! queue ! x264enc ! mux. dbin. ! queue max-size-time=4000000000 ! lamemp3enc ! mux. qtmux name=mux ! filesink location=f"{output_path}"