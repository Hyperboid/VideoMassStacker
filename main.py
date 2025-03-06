import math
import ffmpeg

BATCH_SIZE = 10

def combineFiles(files_list, /,*, index):
    inputs: list[ffmpeg.nodes.InputNode] = [ffmpeg.input(filename) for filename in files_list]
    video: ffmpeg.nodes.FilterNode|ffmpeg.nodes.InputNode = inputs[1]
    for i in range(1, len(inputs)): # Deliberately skipping the first (0th) one
        inp = inputs[i]
        inp = ffmpeg.filter(inp, "colorkey", "0x00FF00", 0.3, 0.2)
        video = ffmpeg.overlay(video, inp)
    audio = ffmpeg.filter([
        st.audio # ffmpeg.filter(st.audio, "volume", 5/BATCH_SIZE)
        for st in inputs
    ], "amix", inputs=len(inputs))
        
        
    stream = ffmpeg.output(audio, video, f"Output/{index}.mp4")
    stream.run()
    ...

def main():
    with open("MasterList.txt") as f:
        files = []
        # Poor man's ipairs
        i = 0
        for line in f:
            i = i + 1
            files.append(line.rstrip())
            if len(files) == BATCH_SIZE:
                combineFiles(files, index = math.ceil(i/BATCH_SIZE))
                files = []
            # if i > 2: break # TODO: Remove limit after testing
        combineFiles(files, index = math.ceil(i/BATCH_SIZE))

if __name__ == "__main__":
    main()