import os
# import os to grab all .mp3 songs from folder

import random
# and random to pick a random song from the song list

import kivy
#import kivy library for UI design
from kivy.app import App
'''from kivymd.uix.relativelayout import MDRelativeLayout'''
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.properties import ObjectProperty

Window.size = (350, 600)

from kivy.core.audio import SoundLoader
# import soundloader to load song in kivy


class MusicScreen(Screen):
    pass

class MainApp(MDApp):
    def build(self):
        self.music_dir = "C:/Users/krit1/Desktop/kmitl/1st/Python/Project/Krit_Worawat/Music Player/Music"
        # self.music_dir is where the music files located

        self.music_files = os.listdir(self.music_dir)
        # self.music_files is the list where restore the music files

        self.music_count = len(self.music_files)
        # self.music_count is count of the music list



        return MusicScreen()

MainApp().run() 