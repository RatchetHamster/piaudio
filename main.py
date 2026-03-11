from timer import Timer
import time
from player import Controller, CoreMixer
from screens import ViewTrack, ViewFolder
from hardware import HardwareController


class App:

    def __init__(self):
        
        CoreMixer().setup() 
        
        # --- Presets ---
        self.vol_notch = 0.05

        # --- Timer ---
        self.sleep_times = [1*60, 2*60, 3*60, 4*60, 5*60]
        self.sleep_index = 1
        self.timer = Timer(
            idle_time=0.5,                                     # minutes until idle
            sleep_time=self.sleep_times[self.sleep_index],     # Default sleep time
            night_start=(22, 00),
            night_end=(6, 0))

        # --- Hardware ---
        self.hardware = HardwareController(
            Ashort_fun=self.A_short,
            Bshort_fun=self.B_short,
            Xshort_fun=self.X_short,
            Yshort_fun=self.Y_short,
            Along_fun=self.A_long,
            Blong_fun=self.B_long,
            Xlong_fun=self.X_long,
            Ylong_fun=self.Y_long
        )

        # --- Screens ---
        self.screens = {
            "ViewTrack": ViewTrack(self, self),
            "ViewFolder": ViewFolder(self, self)}
        self.current_screen = "ViewFolder"

        # --- Library ---
        self.player = Controller(path_str='/home/pi/Music')
        self.set_to_current_folder_view()
        self.show_screen("ViewFolder")


    # ------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------

    def run(self):

        while True:
            # Auto next
            self.player.check_and_autonext() 

            # Screen Refresh
            self.show_screen(self.current_screen)

            # Poll timer/hardware
            self.poll()

            # Drive refresh rate
            time.sleep(0.1)

    def poll(self):
        self.hardware.screen.state = self.timer.state
        if self.hardware.screen.state == "off" and self.player.playing_track is not None:
            self.player.playing_track.stop()
            self.player.playing_track = None

    # ------------------------------------------------
    # SCREEN MANAGEMENT
    # ------------------------------------------------

    def show_screen(self, name):
        self.current_screen = name
        self.screens[name].render()
        self.hardware.screen.display.display(self.screens[name].frame)

    # ------------------------------------------------
    # VIEW HELPERS
    # ------------------------------------------------

    def set_to_current_folder_view(self):

        screen = self.screens["ViewFolder"]
        screen.img_prime_path = self.player.get_indexed_item().path
        self.player.increment_index(1)
        screen.img_next_path = self.player.get_indexed_item().path
        self.player.increment_index(-2)
        screen.img_prev_path = self.player.get_indexed_item().path
        self.player.increment_index(1)
        screen.title_text = self.player.get_indexed_item().name

    def set_to_current_track_view(self):

        screen = self.screens["ViewTrack"]

        start = max(0, self.player.index_within_obj - 3)

        if len(self.player.active_obj.tracks) < 8:
            start = 0
            end = len(self.player.active_obj.tracks)

        elif start + 8 > len(self.player.active_obj.tracks):
            end = len(self.player.active_obj.tracks)
            start = end - 8

        else:
            end = start + 8

        title_list = []

        for i in range(start, start + 8):

            if i >= end:
                title_list.append("")
                continue

            title_list.append(self.player.active_obj.tracks[i].name)

            if self.player.active_obj.tracks[i] == self.player.get_indexed_item():
                bold_index = i - start

        screen.title_list = title_list
        screen.bold_index = bold_index

    def button_choice(self, vf_fun, vt_fun):
        self.timer.nudge_idle()
        if self.player.active_obj.view == "ViewFolder":
            vf_fun()
        else:
            vt_fun()

    # ------------------------------------------------
    # BUTTON FUNCTIONS
    # ------------------------------------------------

    # --- ViewFolder Short Press ---

    def vf_A_short(self):
        self.timer.nudge()
        self.sleep_index = (self.sleep_index + 1) % len(self.sleep_times)
        self.timer.sleep_time = self.sleep_times[self.sleep_index]

    def vf_B_short(self):
        self.player.increment_index(-1)
        self.set_to_current_folder_view()

    def vf_X_short(self):
        self.player.enter_into_index()
        self.player.index_within_obj = 0

        if self.player.active_obj.view == "ViewTrack":
            self.set_to_current_track_view()
            self.show_screen("ViewTrack")
        else:
            self.set_to_current_folder_view()
            self.show_screen("ViewFolder")

    def vf_Y_short(self):
        self.player.increment_index(1)
        self.set_to_current_folder_view()

    # --- ViewTrack Short Press ---

    def vt_A_short(self):
        self.vf_A_short()

    def vt_B_short(self):
        self.player.increment_index(-1)
        self.set_to_current_track_view()

    def vt_X_short(self):
        self.player.enter_into_index()

    def vt_Y_short(self):
        self.player.increment_index(1)
        self.set_to_current_track_view()

    # --- ViewFolder Long Press ---

    def vf_A_long(self):
        if self.timer.state == "off":
            self.timer.is_manual_off = False
            self.timer.nudge()
        else:
            self.timer.is_manual_off = not self.timer.is_manual_off

    def vf_B_long(self):
        CoreMixer().inc_vol(-self.vol_notch)

    def vf_X_long(self):

        self.player.exit_out_of_obj()
        self.player.index_within_obj = 0

        self.set_to_current_folder_view()
        self.show_screen("ViewFolder")

    def vf_Y_long(self):
        CoreMixer().inc_vol(self.vol_notch)

    # --- ViewTrack Long Press ---
    def vt_A_long(self):
        self.vf_A_long()
    def vt_B_long(self):
        self.vf_B_long()
    def vt_X_long(self):
        self.vf_X_long()
    def vt_Y_long(self):
        self.vf_Y_long()

    # ------------------------------------------------
    # GLOBAL BUTTON CALLBACKS
    # ------------------------------------------------
    def A_short(self):
        self.button_choice(self.vf_A_short, self.vt_A_short)
    def B_short(self):
        self.button_choice(self.vf_B_short, self.vt_B_short)
    def X_short(self):
        self.button_choice(self.vf_X_short, self.vt_X_short)
    def Y_short(self):
        self.button_choice(self.vf_Y_short, self.vt_Y_short)
    def A_long(self):
        self.button_choice(self.vf_A_long, self.vt_A_long)
    def B_long(self):
        self.button_choice(self.vf_B_long, self.vt_B_long)
    def X_long(self):
        self.button_choice(self.vf_X_long, self.vt_X_long)
    def Y_long(self):
        self.button_choice(self.vf_Y_long, self.vt_Y_long)


if __name__ == "__main__":
    app = App()
    app.run()