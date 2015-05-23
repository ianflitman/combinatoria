from multiprocessing import Process, Lock, Pool
from subprocess import call, Popen
import cProfile, pstats, StringIO
import time
from functools import wraps

start = time.time()

def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds with %s start offset" %
               (function.func_name, str(t1-t0), str(t0-start))
               )
        return result
    return function_timer

@fn_timer
def concat(output):
    print "called"
    proc = Popen(['/opt/jane_ng/jane_nodejs/ffmpeg-git-20150308-64bit-static/ffmpeg', '-f', 'concat', '-i', '/opt/combinatoria/generator/concatFiles/concat.txt', '-c', 'copy', '-y', output])


@fn_timer
def concatLock(lock,output):
    #lock.acquire()
    print "called"
    proc = call(['/opt/jane_ng/jane_nodejs/ffmpeg-git-20150308-64bit-static/ffmpeg', '-f', 'concat', '-i', '/opt/combinatoria/generator/concatFiles/concat.txt', '-c', 'copy', '-y', output])
    #lock.release()

@fn_timer
def multiConcatProcess():
#if __name__ == '__main__':
    lock = Lock()
    #pool = Pool(3)
    #pool.map(concat, [lock, 'threadConcat.mp4'])
    start = time.time()
    jobs = []
    for num in range(5):
        #p = Process(target=concatLock, args=(lock, 'threadConcat'+str(num)+'.mp4',))
        p = Process(target=concat, args=('threadConcat'+str(num)+'.mp4',))
        jobs.append(p)
        p.start()

    for j in jobs:
        j.join()
        print '%s.exitcode = %s' % (j.name, j.exitcode)
        end = time.time()
        print '{0} finished with {1} start offset'.format(j.name, str(end-start))

def multiConcatPool():
    pass


multiConcatProcess()