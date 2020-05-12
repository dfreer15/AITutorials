from moviepy.editor import *
from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
import librosa


def get_clip():
    main_clip = VideoFileClip("YeKongZhong.mp4")
    my_audio = main_clip.audio
    my_audio.write_audiofile("YKZ_audio.wav")
    return main_clip


def load_audio():
    w, sr = librosa.load("YKZ_audio.wav")
    plt.plot(w)
    plt.show()
    return w, sr


def clean_write_audio(w, sr):

    s = librosa.stft(w)
    ss = np.abs(s)
    angle = np.angle(s)
    b = np.exp(1.0j*angle)

    ns = librosa.stft(w[:8192])
    nss = np.abs(ns)
    mns = np.mean(nss, axis=1)

    sa = ss - mns.reshape((mns.shape[0], 1))
    sa0 = sa * b
    y = librosa.istft(sa0)

    wavfile.write("YKZ_clean2.wav", sr, (y*32768).astype(np.int16))


def write_video(main_clip):
    new_audio = AudioFileClip("YKZ_clean.wav")
    main_clip.audio = new_audio
    main_clip.write_videofile("WoZhiZaihuNi_clean.mp4", codec='mpeg4')


if __name__ == "__main__":
    main_clip = get_clip()
    w, sr = load_audio()
    clean_write_audio(w, sr)
    write_video(main_clip)


