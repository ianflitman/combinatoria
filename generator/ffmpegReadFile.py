
from subprocess import Popen, PIPE
import shlex
import json

ffmpeg_exec = "/opt/jane_ng/jane_nodejs/ffmpeg-git-20150308-64bit-static/ffmpeg"
filePath = '/home/ian/Documents/Jane/mp4/web/mtl'
moviePath = '/f/actor_2o.mp4'

file = "/home/ian/Documents/Jane/mp4/web/mtl/f/actor_2o.mp4"

#command_line = './ffmpeg -i "/home/ian/Documents/Jane/mp4/web/mtl/f/actor_cn.mp4"'
#cmd_line= 'ffprobe -v quiet -print_format json -show_streams /home/ian/Documents/Jane/mp4/web/mtl/f/actor_2o.mp4'
cmd_line= 'ffprobe -v quiet -print_format json -show_streams /opt/combinatoria/generator/titleOutput.mp4'
#cmd_line= 'ffprobe -v quiet -print_format json -show_streams /opt/combinatoria/generator/concatFiles/titleTest.mp4'
args = shlex.split(cmd_line)
print args
#proc = Popen(['ffmpeg', '-i',  '/home/ian/Documents/Jane/mp4/web/mtl/f/actor_cn.mp4'], stdout=PIPE)
proc = Popen(args, stdout=PIPE)
out1, err1 = proc.communicate()
print (out1)
print float(json.loads(out1)['streams'][0]['duration'])
pass
"""
ffmpeg -f lavfi -i color=c=blue:s=320x240:d=0.5 -vf \
"drawtext=fontfile=/path/to/font.ttf:fontsize=30: \
 fontcolor=white:x=(w-text_w)/2:y=(h-text_h-line_h)/2:text='Stack Overflow'" \
output.mp4Married Too LongMarried Too Long
drawtext="fontsize=30:fontfile=FreeSerif.ttf:text='hello world':x=(w-text_w)/2:y=(h-text_h-line_h)/2"
/opt/combinatoria/fonts/UbuntuMono-R.ttf
(main_w/2-text_w/2)


fade=in:0:60 \
-shortest -c:v copy -c:a aac
-i  aevalsrc=0
"""

title_cmd = '/opt/combinatoria/ffmpeg-git-20150308-64bit-static/ffmpeg -f lavfi \
-i color=c=black:s=1920x1080:d=5.5  -b:v 1070k -minrate 1070k -maxrate 1070k -r 25 -vf \
 "[in]drawtext=fontfile=/opt/combinatoria/fonts/UbuntuMono-R.ttf:fontsize=72: \
 fontcolor=white:x=200:y=200:text={0}, \
drawtext=fontfile=/opt/combinatoria/fonts/UbuntuMono-R.ttf:fontsize=32: \
fontcolor=white:x=200:y=500:text={1}, \
drawtext=fontfile=/opt/combinatoria/fonts/UbuntuMono-R.ttf:fontsize=32: \
fontcolor=white:x=200:y=550:text={2}, \
drawtext=fontfile=/opt/combinatoria/fonts/UbuntuMono-R.ttf:fontsize=32: \
fontcolor=white:x=200:y=600:text={3}, \
drawtext=fontfile=/opt/combinatoria/fonts/UbuntuMono-R.ttf:fontsize=32: \
fontcolor=white:x=200:y=650:text={4}, \
drawtext=fontfile=/opt/combinatoria/fonts/UbuntuMono-R.ttf:fontsize=32: \
fontcolor=white:x=200:y=700:text={5}[out]" \
-y output.mp4'.format('Married Too Long',
                   'Generated \t\t\tMay 6th 10.12',
                   'Duration \t\t\t3 min 47 secs',
                   'Camera changes \t\t5',
                   'Dialogue changes \t4',
                   'Made by \t\t\tTom Smith')

args = shlex.split(title_cmd)
title_proc = Popen(args, stdout=PIPE)
title_out = title_proc.communicate()

"""
/opt/combinatoria/generator/silence5s.m4a
"""
mix_silence_cmd = '/opt/combinatoria/ffmpeg-git-20150308-64bit-static/ffmpeg -f lavfi -ar 48000 -ac 2 -f s16le -i /dev/zero \
-i /opt/combinatoria/generator/output.mp4 -shortest -c:v copy -c:a aac \
-strict experimental -color_range 1 -profile:v main -level 42 -b:v 1070k -minrate 1070k -maxrate 1070k -r 25 -bf 1 -vcodec h264 -y /opt/combinatoria/generator/titleOutput.mp4'
mix_silence_cmd2 = '/opt/combinatoria/ffmpeg-git-20150308-64bit-static/ffmpeg -f lavfi -ar 48000 -ac 2 -f s16le -i /opt/combinatoria/generator/silence.aac \
-i /opt/combinatoria/generator/output.mp4  -c:v copy -c:a aac -strict -2\
-profile:v main -level 42 -color_range 1 -b:v 1070k -minrate 1070k -maxrate 1070k -r 25 -bf 1 -vcodec h264 -y /opt/combinatoria/generator/titleOutput.mp4'
args = shlex.split(mix_silence_cmd)
title_proc2 = Popen(args, stdout=PIPE)
title_out2 = title_proc2.communicate()

p = Popen(['MP4Box', '-info', '/home/ian/Documents/Jane/mp4/web/mtl/f/actor_cn.mp4'], stdout=PIPE)
out, err = p.communicate()
durationStr = out[out.index('Duration'): out.index('Fragmented')]
print float(durationStr[durationStr.index('.')-2:])

#out = p.communicate()

#p = Popen(['/opt/jane_ng/jane_nodejs/ffmpeg-git-20150308-64bit-static/ffmpeg', '-i', '/home/ian/Documents/Jane/mp4/web/mtl/f/actor_cn.mp4'], stdout=PIPE)
#out, err = p.communicate()
#print (p.communicate()[0])
#other = p.stdout.read()
#text = p.stdout.read()

# proc = Popen(['ls'], stdout=PIPE)
# cmd = proc.communicate()[0]
# print cmd


pass

