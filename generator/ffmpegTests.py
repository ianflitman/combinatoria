__author__ = 'ian'
import cProfile, pstats, StringIO
from subprocess import Popen, PIPE, call
import shlex
import os
import psutil
import json
import time
from functools import wraps
from memory_profiler import profile
from timeit import timeit
import sys
sys.path.append('/home/ian/Documents/pyvmmonitor/public_api')
#import pyvmmonitor
#pyvmmonitor.connect()

ffmpeg_exec = "/opt/jane_ng/jane_nodejs/ffmpeg-git-20150308-64bit-static/ffmpeg"
concatFilePath = '/opt/combinatoria/generator/concatFiles/concat.txt'

MPBoxConcatString = ""

# /ffmpeg -f concat -i /file/path/to/video/seq.txt -c copy output_filename.mp4
#cmd_line = '{0} -f concat -i {1} -c copy output_filename.mp4'.format(ffmpeg_exec, concatFilePath)
#args = shlex(cmd_line)

def memory_usage_psutil():
    # return the memory usage in MB

    process = psutil.Process(concat('/opt/combinatoria/generator/concatFiles/concat.txt'))
    times = process.get_cpu_times()
    #percent = process.get_cpu_percent(interval=0.1)
    all_mem = process.get_memory_info()
    mem = process.get_memory_info()[0] / float(2 ** 20)
    percent = process.get_cpu_percent(interval=0.1)
    times = process.get_cpu_times()
    return mem, percent

def cpu_percent():
    for x in range(50):
        print psutil.cpu_percent(interval=0.01)#, percpu=True)

def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
               (function.func_name, str(t1-t0))
               )
        return result
    return function_timer

#@pyvmmonitor.profile_method(show_in_pyvmmonitor=True)
def concat(file):
    pr = cProfile.Profile()
    pr.enable()

    #sudo_pwd = 'v1all196'
    #io_command = 'iotop'
    #ioproc = Popen(['sudo','-S', 'iotop'], stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True, universal_newlines=True)
    #print ioproc.communicate('v1all196\n')
    #cpu_percent()
    proc = Popen(['ffmpeg', '-f', 'concat', '-i', file, '-c', 'copy', '-y', 'testConcat.mp4'])
    #cpu_percent()
    #print proc.pid

    #top = Popen(['top', '-d', '0.1', '-p' + os.getpid()], stdout=PIPE, shell=True)
    #top_out = top.communicate()
    #print top_out

    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()
    #print io_out
    #print err
    #ioproc.terminate()
    #out1, err1 = proc.communicate()

@fn_timer
def concatMP4Box(args):
    #args = shlex(cmdStr)
    proc = call(args)

def convertConcatForMP4Box(outputName):
    MPBoxConcatString = 'MP4Box '
    with open('/opt/combinatoria/generator/concatFiles/concat.txt') as fp:
        for line in fp:
            print line
            pathStr = line[line.index('\'' ) +1:line.rfind('\'')]
            MPBoxConcatString += '-cat {0} '.format(pathStr)
    MPBoxConcatString += ' -new {0}'.format(outputName)
    args = shlex.split(MPBoxConcatString)
    return args


@fn_timer
def title():
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
    title_proc = call(args, stdout=PIPE)

def concatTimer():
    print timeit(stmt="call(['/opt/jane_ng/jane_nodejs/ffmpeg-git-20150308-64bit-static/ffmpeg', '-f', 'concat', '-i', '/opt/combinatoria/generator/concatFiles/concat.txt', '-c', 'copy', '-y','testConcat3.mp4'], stdout=PIPE)", setup="from subprocess import Popen, PIPE, call", number=1)
    print 'concatTimer'


if __name__ == "__main__":
    #mp4boxcmd = convertConcatForMP4Box('/opt/combinatoria/generator/testConcat4.mp4')
    #concatMP4Box(mp4boxcmd)
    #startIOLog()
    #cpu_percent()

    #print os.getpid()
    #mem, percent = memory_usage_psutil()
    #print mem
    #print percent
    concat('/opt/combinatoria/generator/concatFiles/concat_f_n.txt')
    #concatTimer()
    #concat('/opt/combinatoria/generator/concatFiles/concatDouble.txt')
    #concat('/opt/combinatoria/generator/concatFiles/concatQuad.txt')
    #title()
    #title()