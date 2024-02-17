#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Description : 酷狗音乐模拟器

import hashlib
import json
import os
import re
import time
import eyed3

import requests


# 获取核心参数signature
def get_signature(client_time, keyword):
    return hashlib.md5(f"NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtbitrate=0callback=callback123clienttime"
                       f"={client_time}clientver=2000dfid=-inputtype=0iscorrection=1isfuzzy=0keyword={keyword}mid"
                       f"={client_time}page=1pagesize=10platform=WebFilterprivilege_filter=0srcappid=2919tag=emuserid"
                       f"=0uuid={client_time}NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt".encode()).hexdigest()


# 获取歌曲列表
def get_song_list(signature, client_time, keyword):
    url = f"https://complexsearch.kugou.com/v2/search/song?callback=callback123&keyword={keyword}&page=1&pagesize=10" \
          "&bitrate=0&isfuzzy=0&tag=em&inputtype=0&platform=WebFilter&userid=0&clientver=2000&iscorrection=1" \
          f"&privilege_filter=0&srcappid=2919&clienttime={client_time}&mid={client_time}&uuid={client_time}&dfid" \
          f"=-&signature={signature}"
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/96.0.4664.55 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'script',
        'Referer': 'https://www.kugou.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    response = requests.request("GET", url, headers=headers)
    response = json.loads(response.text.replace("callback123(", "").replace("})", "}")).get('data').get('lists')
    return response


# 通过hash和album_id获取歌曲播放链接
def get_player_url(client_time, album_id, file_hash, bitrate, hq_file_hash, hq_bitrate):
    if hq_file_hash != '':
        play_url = get_url(hq_file_hash, album_id, client_time)
        if play_url is not None and len(play_url) != 0:
            return play_url, hq_bitrate
    play_url = get_url(file_hash, album_id, client_time)
    if play_url is None:
        return "", 0
    return play_url, bitrate


def get_url(hash_code, album_id, client_time):
    url = f"https://wwwapi.kugou.com/yy/index.php?r=play/getdata&hash={hash_code}&mid" \
          f"=08ea0f85e7e7e866f4f33adb5e3bd40d&album_id={album_id}&_={client_time}"
    headers = {
        'Host': 'wwwapi.kugou.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/96.0.4664.55 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'script',
        'Referer': 'https://www.kugou.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    response = requests.request("GET", url, headers=headers)
    play_url = json.loads(response.text).get('data').get('play_url')
    return play_url


def download(songs):
    if len(songs) == 0:
        return None
    folder_path = "F:\\Administrator\\Music\\"
    while True:
        index = input('请输入下载编号，按回车键搜索（输入0退出）：')
        if index not in songs:
            if index == "0":
                return None
            else:
                print('下载编号有误，请重新输入：')
        else:
            song = songs[index]
            file_path = folder_path + song.get("file_name") + "." + song.get("ext")
            if os.path.exists(file_path):
                print("文件已存在")
            else:
                try:
                    r = requests.get(song.get("url"))
                    f = open(file_path, 'wb')
                    f.write(r.content)
                    f.close()
                except Exception as e:
                    print("Error occurred when downloading file, error message:")
                    print(e)
            # 更新文件信息
            if song.get("ext") == "mp3":
                audio = eyed3.load(file_path)
                year = song.get('publish_time').split("-")[0]
                audio.tag.year = year
                audio.tag.save()


def search(target):
    millis = str(round(time.time() * 1000))
    song_list = get_song_list(get_signature(millis, target), millis, target)
    print('搜索结果如下：')
    songs = {}
    if len(song_list) > 0:
        for i, song in enumerate(song_list, 1):
            r = re.compile(r'<[^>]+>', re.S)
            file_name = r.sub('', song.get('FileName'))
            song_name = r.sub('', song.get('SongName'))
            album_name = song.get('AlbumName')
            album_id = song.get('AlbumID')
            song_url, bit_rate = get_player_url(millis, album_id, song.get('FileHash'), song.get('Bitrate'),
                                                song.get('HQFileHash'), song.get('HQBitrate'))
            singers = []
            for singer in song.get('Singers'):
                singers.append(r.sub('', singer.get('name')))
            # todo album_order = 1
            publish_time = song.get('PublishTime')
            minutes_get, seconds_get = divmod(song.get('Duration'), 60)
            hours_get, minutes_get = divmod(minutes_get, 60)
            duration = (("%d:" % hours_get) if hours_get > 0 else "") + "%02d:%02d" % (minutes_get, seconds_get)
            if song_url != "":
                songs[str(i)] = {"index": i, "song_name": song_name, "duration": duration, "singers": singers,
                                 "album_name": album_name, "album_id": album_id,
                                 # "album_order": album_order,
                                 "publish_time": publish_time, "file_name": file_name, "ext": song.get('ExtName'),
                                 "url": song_url, "bit_rate": bit_rate, "is_original": song.get('IsOriginal')}
        for song in songs:
            print(songs[song])
    else:
        print("很抱歉，未能搜索到相关歌曲信息")
    print()
    return songs


if __name__ == '__main__':
    download(search(input('请输入歌曲名称，按回车键搜索：')))
