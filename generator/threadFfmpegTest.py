import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor as Pool

#info = logging.getLogger(__name__).info

def callback(future):
    if future.exception() is not None:
        logging.info("got exception: %s" % future.exception())
    else:
        logging.info("process returned %d" % future.result())

def main():
    logging.basicConfig(
        level=logging.INFO,
        format=("%(relativeCreated)04d %(process)05d %(threadName)-10s "
                "%(levelname)-5s %(msg)s"))

    # wait for the process completion asynchronously
    logging.info("begin waiting")
    pool = Pool(max_workers=1)
    #f = pool.submit(subprocess.call, "['/opt/combinatoria/ffmpeg-git-20150308-64bit-static/ffmpeg', '-f', 'concat', '-i', '/opt/combinatoria/generator/concatFiles/concat.txt', '-c', 'copy', '-y','testConcat3.mp4']")
    f = pool.submit(subprocess.call, "/opt/combinatoria/ffmpeg-git-20150308-64bit-static/ffmpeg -f concat -i /opt/combinatoria/generator/concatFiles/concat.txt -c copy -y testConcat3.mp4")
    f.add_done_callback(callback)
    pool.shutdown(wait=False) # no .submit() calls after that point
    logging.info("continue waiting asynchronously")

if __name__ == "__main__":
    main()