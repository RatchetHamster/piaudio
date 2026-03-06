import tkinter as tk
from player import Controller, CoreMixer
from screens import ViewTrack, ViewFolder
is_test = True # test mode
if not is_test:
    from hardware import HardwareController

# Startup play
# auto next
# Timer options, power button

# Folder screen: 
# But TL: Power Icon (press to change sleep)
# But TR: list (hold up level, press down level)
# But BL: Left arrow (hold vol down)
# But BR: Right arrow (hold vol up)

# Track: Change Left right to up down (still hold vol up/down)
# List when press, start/stop



class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Presets ---
        self.title("PirateMP3")
        self.vol_notch = 0.05


        # --- Hardware ---
        if not is_test:    
            self.hardware = HardwareController(
                Ashort_fun = self.A_short,
                Bshort_fun = self.B_short,
                Xshort_fun = self.X_short,
                Yshort_fun = self.Y_short,
                Along_fun = self.A_long,
                Blong_fun = self.B_long,
                Xlong_fun = self.X_long,
                Ylong_fun = self.Y_long)
            self.app_w = self.hardware.screen.DISPLAY_W
            self.app_h = self.hardware.screen.DISPLAY_H
        else:
            self.app_w, self.app_h = (240,240)
        self.geometry(f'{self.app_w}x{self.app_h}')

        # --- Screens & Frames ---
        self.mainframe = tk.Frame(self, bg='SlateGray2')
        self.mainframe.pack(fill='both', expand=True)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)

        self.screens = {}
        screen_classes = (ViewTrack, ViewFolder)

        for ScreenClass in screen_classes:
            screen_name = ScreenClass.__name__
            frame = ScreenClass(self.mainframe, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.screens[screen_name] = frame
        

        # --- Library ---
        self.player = Controller(path_str=r'D:\Media\Audiobooks\AudiobookPi')
        self.set_to_current_folder_view()
        self.show_screen("ViewFolder")

        # --- Header ---
        CoreMixer().setup()
        self.set_vol_str()
        #self.poll_timer()

    # --- App Polling ---
    def poll_timer(self):
        time_to_off = self.hardware.timer.time_until_off
        if time_to_off is not None:
            hours = int(time_to_off // 3600)
            minutes = int((time_to_off % 3600) // 60)
            time_str = f"{hours:02d}:{minutes:02d}"
        for screen in self.screens.values():
            screen.time_to_sleep_str = time_str

        self.after(1000, self.poll_timer)

    # --- Helper Functions ---

    def show_screen(self, name):
        """Raise the selected screen to the top."""
        frame = self.screens[name]
        frame.tkraise()

    def set_to_current_folder_view(self):
        self.screens["ViewFolder"].img_prime_path = self.player.get_indexed_item().path
        self.player.increment_index(1)
        self.screens["ViewFolder"].img_next_path = self.player.get_indexed_item().path
        self.player.increment_index(-2)
        self.screens["ViewFolder"].img_prev_path = self.player.get_indexed_item().path
        self.player.increment_index(1)
        self.screens["ViewFolder"].title_text = self.player.get_indexed_item().name
    
    def set_to_current_track_view(self):
        start = max(0, self.player.index_within_obj-3)
        if len(self.player.active_obj.tracks) < 8:
            start = 0
            end = len(self.player.active_obj.tracks)
        elif start+8 > len(self.player.active_obj.tracks):
            end = len(self.player.active_obj.tracks)
            start = end-8
        else:
            end = start+8
        title_list = []

        for i in range(start, start+8):
            if i >= end:
                title_list.append('')
                continue          
            title_list.append(self.player.active_obj.tracks[i].name)
            if self.player.active_obj.tracks[i] == self.player.get_indexed_item():
                bold_index = i-start
        self.screens["ViewTrack"].title_list = title_list
        self.screens["ViewTrack"].bold_index = bold_index
            
    
    def set_vol_str(self):
        vol = CoreMixer().get_vol()
        for screen in self.screens.values():
            screen.vol_str = f"{vol*100:.0f}%"
    
    def button_choice(self, vf_fun, vt_fun):
        if self.player.active_obj.view == "ViewFolder":
            vf_fun()
        else:
            vt_fun()
    
    # -------- BUTTON FUNCTIONS -------- #

    # --- ViewFolder Short Press Functions ---

    def vf_A_short(self):
        # power icon, change sleep mode
        pass

    def vf_B_short(self):
        # Button (BL) - left arrow (hold vol down)
        self.player.increment_index(-1)
        self.set_to_current_folder_view()

    def vf_X_short(self):
        # Button (TR) - list (hold up level, press down level)
        self.player.enter_into_index()
        self.player.index_within_obj = 0
        if self.player.active_obj.view == "ViewTrack":
            self.set_to_current_track_view()
            self.show_screen("ViewTrack")
        else:
            self.set_to_current_folder_view()
            self.show_screen("ViewFolder")
    
    def vf_Y_short(self):
        # Button (BR) - right arrow (hold vol up)
        self.player.increment_index(1)
        self.set_to_current_folder_view()
    
    # --- ViewTrack Short Press Functions ---

    def vt_A_short(self):
        # power icon, change sleep mode
        pass

    def vt_B_short(self):
        # Button (BL) - down arrow (hold vol down)
        self.player.increment_index(-1)
        self.set_to_current_track_view()
    
    def vt_X_short(self):
        # Button (TR) - list (hold up level, press start/stop)
        # Need to do this so it works with Thread!
        if CoreMixer().is_busy():
            self.player.playing_track.stop()
        else:
            self.player.playing_track.play()

    def vt_Y_short(self):
        # Button (BR) - up arrow (hold vol up)
        self.player.increment_index(1)
        self.set_to_current_track_view()

    # --- ViewFolder Long Press Functions ---

    def vf_A_long(self):
        # power icon, change sleep mode
        pass

    def vf_B_long(self):
        # Button (BL) - left arrow (hold vol down)
        CoreMixer().inc_vol(-self.vol_notch)
        self.set_vol_str()
    
    def vf_X_long(self):
        # Button (TR) - list (hold up level, press down level)
        self.player.exit_out_of_obj()
        self.player.index_within_obj = 0
        self.set_to_current_folder_view()
        self.show_screen("ViewFolder")
    
    def vf_Y_long(self):
        # Button (BR) - right arrow (hold vol up)
        CoreMixer().inc_vol(self.vol_notch)
        self.set_vol_str()
    
    # --- ViewTrack Long Press Functions ---

    def vt_A_long(self):
        # power icon, change sleep mode
        pass

    def vt_B_long(self):
        # Button (BL) - down arrow (hold vol down)
        self.vf_B_long()
    
    def vt_X_long(self):
        # Button (TR) - list (hold up level, press start/stop)
        self.vf_X_long()
    
    def vt_Y_long(self):
        # Button (BR) - up arrow (hold vol up)
        self.vf_Y_long()
    
    # --- Global Button Functions (called by hardware) --- #

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
    app.Y_short()
    #app.Y_short()
    app.X_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    #app.Y_short()
    app.X_long()
    app.B_short()

    print(app.player.get_indexed_item().name)
    app.mainloop()

        

