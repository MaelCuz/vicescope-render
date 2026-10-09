#!/usr/bin/env python3
"""ViceScope first cloud render. Uses owned narration and generated graphics."""
import os, subprocess, json, pathlib
ROOT=pathlib.Path(__file__).parent
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
AUDIO=ROOT/'assets/narration.wav'
if not AUDIO.exists(): raise SystemExit('Missing assets/narration.wav')
def cmd(*args):
    print('Running:', ' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),check=True)
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(AUDIO)]).decode().strip())
# No misleading factual imagery: animated original gradient-ish background and headline.
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
lines=[('GTA VI','NEWS UPDATE'),('NEW MERCH','REPORTED'),('MACCA','THE GATOR'),('VICESCOPE','DEMO VIDEO')]
filters=[]
for i,(a,b) in enumerate(lines):
    start=i*duration/len(lines); end=(i+1)*duration/len(lines)
    for label,y,size,color in [(a,650,110,'white'),(b,840,65,'yellow')]:
        safe=label.replace(':','\\:').replace("'","\\'")
        filters.append(f"drawtext=fontfile={font}:text='{safe}':fontcolor={color}:fontsize={size}:x=(w-text_w)/2:y={y}:enable='between(t,{start:.3f},{end:.3f})'")
filters.append(f"drawtext=fontfile={font}:text='VICESCOPE  /  EDITORIAL TEST':fontcolor=white@0.8:fontsize=35:x=(w-text_w)/2:y=1760")
# 540x960 demo to keep free runners light; output 1080x1920 scaled.
video_filter='scale=1080:1920,'+','.join(filters)+',format=yuv420p'
cmd('ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i',f'color=c=0x101b35:s=540x960:r=24:d={duration:.3f}','-i',AUDIO,'-filter_complex','[0:v]'+video_filter+'[v]','-map','[v]','-map','1:a','-c:v','libx264','-preset','veryfast','-crf','27','-c:a','aac','-b:a','128k','-t',str(duration),'-movflags','+faststart',OUT/'vicescope-test.mp4')
print(json.dumps({'output':str(OUT/'vicescope-test.mp4'),'duration':duration}))
