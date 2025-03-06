import math
import sys
import os
import ffmpeg

BATCH_SIZE = 10

def combineFiles(files_list, /,*, output):
    inputs: list[ffmpeg.nodes.InputNode] = [ffmpeg.input(filename) for filename in files_list]
    video: ffmpeg.nodes.FilterNode|ffmpeg.nodes.InputNode = inputs[1]
    for i in range(1, len(inputs)): # Deliberately skipping the first (0th) one
        inp = inputs[i]
        inp = ffmpeg.filter(inp, "colorkey", "0x00FF00", 0.1, 0.1)
        video = ffmpeg.overlay(video, inp)
    audio = ffmpeg.filter([
        st.audio # ffmpeg.filter(st.audio, "volume", 5/BATCH_SIZE)
        for st in inputs
    ], "amix", inputs=len(inputs))
        
        
    stream = ffmpeg.output(audio, video, output)
    stream.run()
    ...

def main(argv):
    list_path = "MasterList.txt"
    output_path = "Output"
    if len(argv) > 1:
        list_path = argv[1]
        if os.path.isdir(argv[1]):
            list_path = list_path + "/PhaseList.txt"
    if len(argv) > 2:
        output_path = argv[2]

    with open(list_path) as f:
        processPhase(f, output=output_path)

def processPhase(l, /,*, output="Output"):
    files = []
    # Poor man's ipairs
    i = 0
    for line in l:
        if len(line.strip()) < 1: break
        i = i + 1
        files.append(line.rstrip())
        if len(files) == BATCH_SIZE:
            combineFiles(files, output = f"{output}/{math.ceil(i/BATCH_SIZE)}.mp4")
            files = []
        # if i > 18: break # TODO: Remove limit after testing
    # Combine leftovers
    if len(files) > 0:
        i = i + 1
        combineFiles(files, output = f"{output}/{math.ceil(i/BATCH_SIZE)}.mp4")
    with open(f"{output}/PhaseList.txt", "w") as f:
        for j in range(1, math.ceil(i/BATCH_SIZE)+1):
            f.write(f"{output}/{j}.mp4\n")


if __name__ == "__main__":
    main(sys.argv)