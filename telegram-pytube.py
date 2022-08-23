import requests
import json
import time
from pytube import YouTube
import re
import os
import subprocess

def read_msg(offset):
    data = {
        "offset": offset,
    }
    resp = requests.get(base_url+'/getUpdates', data=data)
    dataframe = resp.json()

    for i in dataframe["result"]:
        try:
            print(i["message"]["text"])
            yt = YouTube(i["message"]["text"])
            if len(yt.streams) > 0:
                f = open(i["message"]["from"]["username"] + '.txt', 'w')
                f.write(i["message"]["text"])
                f.close()

                keyboard = [[{"text": "Audio"}]]
                keyboard_res = [[{"text": "144p"}], [{"text": "240p"}], [{"text": "360p"}], [{"text": "480p"}], [{"text": "720p"}], [{"text": "1080p"}], [{"text": "1440p"}], [{"text": "2160p"}]]

                for k in range(8):
                    if yt.streams.filter(res=formats[k+1]):
                        keyboard.append(keyboard_res[k])

                send_download(i["message"]["from"]["id"], keyboard)
            else:
                send_message(i["message"]["from"]["id"], 'Can not download this video')

        except:
            try:
                if i["message"]["text"] in formats:
                    f = open(i["message"]["from"]["username"] + '.txt')
                    link = f.readline()
                    f.close()

                    yt = YouTube(link)
                    title = re.sub(r"[^a-zA-Z0-9 ]", "", yt.title)
                    username = i["message"]["from"]["username"] + '/'

                    try:
                        os.mkdir(username)
                    except:
                        pass
                    
                    # Downloading audio
                    input_audio = username + title + ' - audio'
                    try:
                        audio = yt.streams.filter(abr='128kbps')
                        audio[0].download(filename = input_audio)
                    except:
                        audio = yt.streams.filter(type='audio')
                        audio[0].download(filename = input_audio)

                    if i["message"]["text"] == 'Audio':
                        # Converting audio
                        output_media = username + title + ' - ' + i["message"]["text"] + '.mp3'
                        subprocess.call(["ffmpeg", "-i", input_audio, output_media, "-y"])
                        os.remove(input_audio)
                        size = round(os.path.getsize(output_media) / 1024 / 1024, 2)

                        if size > 50:
                            send_message(i["message"]["from"]["id"], 'Done! ' + str(size) + 'MB')
                        else:
                            send_audio(i["message"]["from"]["id"], output_media)

                    else:
                        # Downloading video and merging
                        input_video = username + title + ' - video'
                        video = yt.streams.filter(res=i["message"]["text"])
                        video[0].download(filename = input_video)

                        output_media = username + title + ' - ' + i["message"]["text"] + '.mp4'
                        subprocess.call(["ffmpeg", "-i", input_video, "-i", input_audio, "-c", "copy", output_media, "-y"])
                        os.remove(input_video)
                        os.remove(input_audio)
                        size = round(os.path.getsize(output_media) / 1024 / 1024, 2)

                        if size > 50:
                            send_message(i["message"]["from"]["id"], 'Done! ' + str(size) + 'MB')
                        else:
                            send_video(i["message"]["from"]["id"], output_media)

            except:
                pass

    if dataframe["result"]:
        return dataframe["result"][-1]["update_id"] + 1

def send_download(user, keyboard):
    base_url_download = base_url + '/sendMessage'
    headers = {"Content-Type": "application/json"}
    data = {
        "chat_id": user,
        "text": "Select option",
        "reply_markup": {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": True,
            }
        }
    data = json.dumps(data)
    resp = requests.post(base_url_download, data=data, headers=headers)

def send_message(user, message):
    base_url_message = base_url + '/sendMessage'
    headers = {"Content-Type": "application/json"}
    data = {
        "chat_id": user,
        "text": message,
        }

    data = json.dumps(data)
    resp = requests.post(base_url_message, data=data, headers=headers)

def send_audio(user, audio):
    base_url_audio = base_url + '/sendAudio'
    audio = open(audio, 'rb')
    data = {
        "chat_id": user
        }
    files = {
        "audio": audio
    }
    resp = requests.get(base_url_audio, data=data, files=files)

def send_video(user, video):
    base_url_video = base_url + '/sendVideo'
    video = open(video, 'rb')
    data = {
        "chat_id": user
        }
    files = {
        "video": video
    }
    resp = requests.get(base_url_video, data=data, files=files)

############################################

base_url = 'https://api.telegram.org/botxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
offset = 0
formats = ['Audio', '144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p']

while True:
    try:
        offset = read_msg(offset)
    except:
        pass
    time.sleep(1)
