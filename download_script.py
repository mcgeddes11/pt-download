from pytube import YouTube
from argparse import ArgumentParser
import os
import time
"https://www.youtube.com/watch?v=tAGnKpE4NCI"

if __name__ == "__main__":
    RETRY_COUNT = 5

    # Deal with input arguments
    parser = ArgumentParser(description="Download a video from Youtube")
    parser.add_argument("url", type=str, help="URL of the video to be downloaded")
    parser.add_argument("--format", type=str, help="Format to download (optional). Options are: 'audio', 'video' (default)")

    args = parser.parse_args()

    url = args.url
    format = args.format

    # This is finnicky, try a few times
    retries = 0
    mov = None
    while mov is None and retries < RETRY_COUNT:
        try:
            mov = YouTube(url)
        except Exception as e:
            retries += 1
            time.sleep(1)
            if retries >= RETRY_COUNT:
                raise(e)

    if format is not None and format not in ["video", "audio"]:
        raise Exception("Invalid format specified: {}".format(format))

    if format is None or format == "video":
        pth = mov.streams.get_highest_resolution().download()
        print("Video extracted to: {}".format(pth))
    else:
        pth = mov.streams.get_audio_only().download()
        print("Audio extracted to: {}".format(pth))



