import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
import yt_dlp

MUSIC_DIR = "astama_music"
if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)

class AstamaUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=10, **kwargs)
        self.sound = None

        self.add_widget(Label(text="ASTAMA MUSIC", font_size='22sp', bold=True, size_hint_y=None, height=40, color=(0.48, 0.36, 1, 1)))
        
        self.url_input = TextInput(hint_text="Paste YouTube URL here...", multiline=False, size_hint_y=None, height=45)
        self.add_widget(self.url_input)

        self.btn_download = Button(text="DOWNLOAD FOR OFFLINE", size_hint_y=None, height=50, background_color=(0.48, 0.36, 1, 1))
        self.btn_download.bind(on_press=self.start_download)
        self.add_widget(self.btn_download)

        self.status_lbl = Label(text="Status: Ready", size_hint_y=None, height=30, color=(0.7, 0.7, 0.7, 1))
        self.add_widget(self.status_lbl)

        self.scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        self.add_widget(self.scroll)

        controls = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.btn_play = Button(text="PLAY", background_color=(0, 0.8, 0.4, 1))
        self.btn_play.bind(on_press=self.play_music)
        controls.add_widget(self.btn_play)

        self.btn_stop = Button(text="STOP", background_color=(1, 0.3, 0.3, 1))
        self.btn_stop.bind(on_press=self.stop_music)
        controls.add_widget(self.btn_stop)

        self.add_widget(controls)
        self.selected_file = None
        self.refresh_list()

    def refresh_list(self):
        self.list_layout.clear_widgets()
        files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.m4a', '.webm', '.ogg', '.wav'))]
        for f in files:
            btn = Button(text=f, size_hint_y=None, height=40, background_color=(0.2, 0.2, 0.25, 1))
            btn.bind(on_press=lambda instance, filename=f: self.select_file(filename, instance))
            self.list_layout.add_widget(btn)

    def select_file(self, filename, instance):
        self.selected_file = os.path.join(MUSIC_DIR, filename)
        self.status_lbl.text = f"Selected: {filename[:20]}..."

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.status_lbl.text = "Please enter URL first!"
            return
        self.status_lbl.text = "Downloading..."
        self.btn_download.disabled = True
        threading.Thread(target=self.download_thread, args=(url,), daemon=True).start()

    def download_thread(self, url):
        opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(MUSIC_DIR, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'quiet': True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.status_lbl.text = "Download Complete!"
            self.url_input.text = ""
        except Exception as e:
            self.status_lbl.text = "Download Failed!"
        self.btn_download.disabled = False
        self.refresh_list()

    def play_music(self, instance):
        if not self.selected_file:
            self.status_lbl.text = "Select a song first!"
            return
        if self.sound:
            self.sound.stop()
        self.sound = SoundLoader.load(self.selected_file)
        if self.sound:
            self.sound.play()
            self.status_lbl.text = "Playing..."

    def stop_music(self, instance):
        if self.sound:
            self.sound.stop()
            self.status_lbl.text = "Stopped"

class AstamaApp(App):
    def build(self):
        return AstamaUI()

if __name__ == '__main__':
    AstamaApp().run()
      
