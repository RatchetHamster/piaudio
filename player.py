import os
import threading
import time
from pygame import mixer
from pathlib import Path

""" The Structure of the library needs to be strict! If it constains a folder, any 
other tracks in that folder will be discounted. Tracks need to have no folders inside the 
folder they rest in. All artwork at each level should be a jpg. 
    e.g. Artist folder > album subfolders (with artist jpg) > tracks (with album jpg)"""

# Select HiFiBerry DAC before importing mixer
os.environ['SDL_AUDIODRIVER'] = 'alsa'
os.environ['SDL_ALSA_DEV'] = 'plughw:1,0'

class CoreMixer:
    def setup(self):
        """Initialize mixer and start with max volume."""
        if not mixer.get_init():
            mixer.init()
        mixer.music.set_volume(0.75)  # Start at 75% volume

    def load(self, path_str):
        mixer.music.load(path_str)

    def play(self):
        mixer.music.play()

    def stop(self):
        mixer.music.stop()

    def is_busy(self):
        return mixer.music.get_busy()

    def inc_vol(self, amount):
        """Increase or decrease volume. Clamped between 0.0 and 1.0."""
        current = mixer.music.get_volume()
        new_vol = max(0.0, min(1.0, current + amount))
        mixer.music.set_volume(new_vol)

    def get_vol(self):
        """Return current software volume (0.0 to 1.0)."""
        return mixer.music.get_volume()
    
class Track():
    def __init__(self, path: Path, parent=None):
        self.path = path
        self.name = self.path.stem
        self.parent = parent
    
    def play(self):
        CoreMixer().load(str(self.path))
        CoreMixer().play()
    
    def stop(self):
        CoreMixer().stop()
    

class StructuredFolder():
    def __init__(self, path: Path, parent=None):
        # --- Base --- 
        self.path = path
        self.name = path.stem
        self.parent = parent
        self.art_path = self.get_art_path(path)

        self.subfolders = self.get_subfolders(path) # list of StructuredFolders (or None if empty)
        self.tracks = self.get_tracks(path) # list of Tracks (or None if empty)

    @property
    def view(self):
        return "ViewFolder" if self.subfolders is not None else "ViewTrack"
    
    # --- Methods ---
    def get_art_path(self, path):
        jpgs = list(self.path.glob("*.jpg"))
        return jpgs[0] if len(jpgs)!=0 else None
    
    def get_subfolders(self, path: Path):
        folders = sorted(
            [p for p in path.iterdir() if p.is_dir()],
            key=lambda p: p.name.lower()
        )
        folder_list = [StructuredFolder(p, self) for p in folders]
        return folder_list if len(folder_list) != 0 else None

    def get_tracks(self, path: Path):
        track_list = [Track(p, self) for p in sorted(list(path.glob("*.mp3")))]
        return track_list if len(track_list)!=0 else None


class Controller(StructuredFolder):
    def __init__(self, path_str: str):
        super().__init__(Path(path_str))
        self.active_obj = self
        self.index_within_obj = 0
        self.playing_track = None

    # --- Methods ---
    def enter_into_index(self):
        """ If the index object within active_bj structure is a folder, it will go down a level. 
        if it is a track it will start playing."""
        if self.active_obj.view == "ViewFolder":
            self.active_obj = self.active_obj.subfolders[self.index_within_obj]
        else:
            if self.playing_track is not None and self.playing_track == self.active_obj.tracks[self.index_within_obj]:
                self.playing_track.stop()
                self.playing_track = None
            else:
                self.playing_track = self.active_obj.tracks[self.index_within_obj]
                self.playing_track.play()

    
    def exit_out_of_obj(self):
        """If this is the controller level (i.e. None parent) it will do nothing."""
        if self.active_obj.parent is not None: 
            self.active_obj = self.active_obj.parent

    def increment_index(self, inc_amount):
        #inc amount can be positive or negative
        self.index_within_obj += inc_amount
        length = len(self.active_obj.subfolders) if self.active_obj.subfolders is not None else len(self.active_obj.tracks)
        self.index_within_obj %= length
    
    def get_indexed_item(self):
        if self.active_obj.view == "ViewFolder":
            return self.active_obj.subfolders[self.index_within_obj]
        else:
            return self.active_obj.tracks[self.index_within_obj]
    
    def check_and_autonext(self):
        """If the current track has finished playing, it will move to the next one and play it."""
        if self.playing_track is not None and not CoreMixer().is_busy():
            i = self.playing_track.parent.tracks.index(self.playing_track) + 1 % len(self.playing_track.parent.tracks)
            if i == 0:
                self.playing_track = None
            else:
                self.playing_track = self.playing_track.parent.tracks[i]
                self.playing_track.play()
        

if __name__ == "__main__":
    CoreMixer().setup()
    controller = Controller(r'D:\Media\Audiobooks\AudiobookPi')
    controller.increment_index(2)
    print(controller.active_obj.view)
    controller.enter_into_index()
    print(controller.active_obj.view)
    print(controller.active_obj.name)
    print(controller.active_obj.subfolders)
    #controller.exit_out_of_obj()
    if controller.active_obj.subfolders is not None:
        for folder in controller.active_obj.subfolders:
            print(folder.name)
    if controller.active_obj.tracks is not None:
        for track in controller.active_obj.tracks:
            print(track.name)