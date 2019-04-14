from cueparser import CueSheet
from cueparser import CueTrack
from cueparser import offsetToTimedelta
import json
import argparse
import sys
import shlex
from subprocess import Popen, PIPE

def fileFormat(cueFormat):
    if cueFormat == "WAVE":
        return ".wav"
    elif cueFormat == "MP3":
        return ".mp3"
    elif cueFormat == "AIFF":
        return ".aiff"
    elif cueFormat == "BINARY":
        return ".bin"
    else:
        return ".wav"

parser = argparse.ArgumentParser()
parser.add_argument("file", help="path to cue file")
args = parser.parse_args()

cuesheet = CueSheet()
cuesheet.setOutputFormat("%performer% - %title%\n%file%\n%tracks%", "%title%")
cuefile = args.file
with open(cuefile, "rb") as f:
    cuesheet.setData(f.read().decode(sys.stdout.encoding))

cuesheet.parse()

ffprobeCmd = "ffprobe -print_format json -show_format -sexagesimal aonatsu-ost-a.flac"

process = Popen(shlex.split(ffprobeCmd), stdout=PIPE, stderr=PIPE)
out = process.communicate()
exit_code = process.wait()

ffprobe_out = json.loads(out[0].decode("utf-8"))
end_time = ffprobe_out["format"]["duration"]
end_time = end_time[2:-4].replace(".", ":")

for t in cuesheet.tracks:
    ffmpegCmd = ""
    print("Extracting " + t.title)
    sys.stdout.flush()
    if t.duration is not None:
        ffmpegCmd = "ffmpeg -y -i " + cuesheet.file + " -ss " + str(offsetToTimedelta(t.offset)) + " -t " + str(t.duration) + " " + t.title + fileFormat(cuesheet.aformat)
    else:
        duration = offsetToTimedelta(end_time) - offsetToTimedelta(t.offset)
        ffmpegCmd = "ffmpeg -y -i " + cuesheet.file + " -ss " + str(offsetToTimedelta(t.offset)) + " -t " + str(duration) + " " + t.title + fileFormat(cuesheet.aformat)

    process = Popen(shlex.split(ffmpegCmd), stdout=PIPE, stderr=PIPE)
    out = process.communicate()
    exit_code = process.wait()
    

