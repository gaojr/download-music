#!/usr/bin/python
# -*- coding: utf-8 -*-

import CloudMusic
import KuGouMusic
import KuWoMusic


def search(song_name):
    songs = CloudMusic.search(song_name)
    if not songs:
        CloudMusic.download(songs)
    else:
        songs = KuGouMusic.search(song_name)
        if not songs:
            KuGouMusic.download(songs)
        else:
            songs = KuWoMusic.search(song_name)
            if not songs:
                KuWoMusic.download(songs)


if __name__ == '__main__':
    search(input('请输入歌曲名称，按回车键搜索：'))
