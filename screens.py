import tkinter as tk
from PIL import Image, ImageTk
import os
from pathlib import Path

class ViewBase(tk.Frame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.parent = parent

        # --- Canvas ---
        self.canvas = tk.Canvas(self, bg=self["bg"])
        self.canvas.pack(fill='both', expand=True)

        # --- Draw Icon Backdrops ---
        self.draw_icons("icon-backdrop", rotation=0, pos="nw")
        self.draw_icons("icon-backdrop", rotation=0, pos="sw")
        self.draw_icons("icon-backdrop", rotation=180, pos="ne")
        self.draw_icons("icon-backdrop", rotation=180, pos="se")

        # --- Fonts ---
        self.font= ("Helvetica", 15, "bold")
        self.font_sm= ("Helvetica", 10, "bold")

        # --- Setters ---
        self._vol_str = '-- %'
        self._time_to_sleep_str = "--:--"

        # --- Header ---
        self.vol_label = tk.Label(self, text=self.vol_str, bg=self.parent["bg"], fg="black", font=self.font)
        self.vol_label.place(relx=1.0, x=-3, y=3, anchor="ne")

        self.time_to_sleep_label = tk.Label(self, text=self._time_to_sleep_str, bg=self.parent["bg"], fg="black", font=self.font)
        self.time_to_sleep_label.place(relx=0.5, y=3, anchor="n")

    @property
    def vol_str(self):
        return self._vol_str

    @vol_str.setter
    def vol_str(self, value):
        self._vol_str = value
        self.vol_label.config(text=value)

    @property
    def time_to_sleep_str(self):
        return self._time_to_sleep_str
    
    @time_to_sleep_str.setter
    def time_to_sleep_str(self, value):
        self._time_to_sleep_str = value
        self.time_to_sleep_label.config(text=value)

    def draw_icons(self, icon_name_str, rotation, pos, h_pad=47, w_pad=0):
        """ icon_name_str = filename (without .png)
            rotation = rotation in degrees (clockwise)
            pos = "nw, ne, sw, se" """

        img = Image.open(os.path.join("resources", f'{icon_name_str}.png')).convert("RGBA")
        img = img.rotate(rotation, expand=True)
        if icon_name_str != "icon-backdrop":
            alpha = img.getchannel("A")
            solid_color = Image.new("RGBA", img.size, (255,255,255))
            img = Image.composite(solid_color, img, alpha)

        img = ImageTk.PhotoImage(img)
        
        # Keep reference (prevent garbage collection)
        if not hasattr(self.canvas, "_image_refs"):
            self.canvas._image_refs = []
        self.canvas._image_refs.append(img)

        if pos == "nw":
            x = w_pad
            y = h_pad
        elif pos == "ne":
            x = 240 - w_pad
            y = h_pad
        elif pos == "sw":
            x = w_pad
            y = 240 - h_pad
        elif pos == "se":
            x = 240 - w_pad
            y = 240 - h_pad

        self.canvas.create_image(x,y, image=img, anchor=pos)


class ViewFolder(ViewBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, bg=parent["bg"])

        # --- Draw Icons ---
        self.draw_icons("icon-time-onoff", rotation=0, pos="nw", h_pad=50, w_pad=3)
        self.draw_icons("icon-rightarrow", rotation=180, pos="sw", h_pad=50, w_pad=3)
        self.draw_icons("icon-list", rotation=0, pos="ne", h_pad=50, w_pad=3)
        self.draw_icons("icon-rightarrow", rotation=0, pos="se", h_pad=50, w_pad=3)

        # --- Default Albumn ---
        img = Image.open(r'resources/default_cover.png')
        self.default_art = ImageTk.PhotoImage(img.resize((100,100), Image.LANCZOS))
        self.default_art_sm = ImageTk.PhotoImage(img.resize((60,60), Image.LANCZOS))

        # --- Labels ---
        self.label_prev = tk.Label(self, image=self.default_art_sm, bd=0)
        self.label_prev.image = self.default_art_sm
        self.label_prev.place(x=5, rely=0.5, anchor="w")

        self.label_prime = tk.Label(self, image=self.default_art, bd=0)
        self.label_prime.image = self.default_art
        self.label_prime.place(relx=0.5, rely=0.5, anchor="center")

        self.label_next = tk.Label(self, image=self.default_art_sm, bd=0)
        self.label_next.image = self.default_art_sm
        self.label_next.place(relx=1.0, x=-5, rely=0.5, anchor="e")

        self.title_label = tk.Label(self, text='Nothing Yet', bg=self.parent["bg"], fg="black", font=self.font_sm, wraplength=150, justify="center")
        self.title_label.place(relx=0.5, rely=1.0, y=-70, anchor="n")

        # --- SETTERS ---
        self._img_prime_path = None
        self._img_prev_path = None
        self._img_next_path = None
        self._title_text = None

    # --- Setters ---
    @property
    def img_prime_path(self):
        return self._img_prime_path
    @img_prime_path.setter
    def img_prime_path(self, value):
        self._img_prime_path = value
        if value is None:
            self.label_prime.config(image=self.default_art)
            self.label_prime.image = self.default_art
        else:
            tk_img = self._load_image(value, size=(100,100))
            self.label_prime.config(image=tk_img)
            self.label_prime.image = tk_img
        
    @property
    def img_prev_path(self):
        return self._img_prev_path
    @img_prev_path.setter
    def img_prev_path(self, value):
        self._img_prev_path = value
        if value is None:
            self.label_prev.config(image=self.default_art_sm)
            self.label_prev.image = self.default_art_sm
        else:
            tk_img = self._load_image(value, size=(60,60))
            self.label_prev.config(image=tk_img)
            self.label_prev.image = tk_img

    @property
    def img_next_path(self):
        return self._img_next_path
    @img_next_path.setter
    def img_next_path(self, value):
        self._img_next_path = value
        if value is None:
            self.label_next.config(image=self.default_art_sm)
            self.label_next.image = self.default_art_sm
        else:
            tk_img = self._load_image(value, size=(60,60))
            self.label_next.config(image=tk_img)
            self.label_next.image = tk_img
    
    @property
    def title_text(self):
        return self._title_text

    @title_text.setter
    def title_text(self, value):
        self._title_text = value
        if value==None:
            self.title_label.config(text='')
        else:
            self.title_label.config(text=value)
    
    # --- Helpers ---
    def _load_image(self, path: Path, size=(100,100)):
        if path is None:
            return None
        path = path / "cover.jpg"
        if path.exists():
            img = Image.open(path)
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None
    

class ViewTrack(ViewBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, bg=parent["bg"])

        # --- Draw Icons ---
        self.draw_icons("icon-time-onoff", rotation=0, pos="nw", h_pad=50, w_pad=3)
        self.draw_icons("icon-rightarrow", rotation=270, pos="sw", h_pad=50, w_pad=3)
        self.draw_icons("icon-list", rotation=0, pos="ne", h_pad=50, w_pad=3)
        self.draw_icons("icon-rightarrow", rotation=90, pos="se", h_pad=50, w_pad=3)

        # --- Track List ---
        self.title_labels = []
        for i in range(8):
            self.title_labels.append(tk.Label(self, text='', bg=self.parent["bg"], fg="black", font=self.font_sm, anchor="nw", justify="left"))
            self.title_labels[-1].place(x=35, y=35 + i*25, anchor="nw", width = 170)
        self._title_list = [] #list of strings of track titles
        self._bold_index = None # Index to make bold 
    
    @property
    def title_list(self):
        return self._title_list
    
    @title_list.setter
    def title_list(self, value):
        self._title_list = value
        self.bold_index = None
        for i, label in enumerate(self.title_labels):
            if i<len(value):
                label.config(text=value[i])
            else:
                label.config(text='')
    
    @property
    def bold_index(self):
        return self._bold_index
    
    @bold_index.setter
    def bold_index(self, value):
        if self._bold_index != None:
            self.title_labels[self._bold_index].config(bg=self.parent["bg"])
        self._bold_index = value
        if value != None:
            self.title_labels[value].config(bg="SlateGray3")



if __name__ == "__main__":
    root = tk.Tk()
    root.title("ViewBase Test")
    root.geometry("240x240")  # adjust as needed
    root.config(bg='SlateGray2')

    # Dummy controller (since ViewBase expects one)
    class DummyController:
        def show_screen(self, name):
            print(f"Switching to {name}")

    controller = DummyController()

    # Create and pack the test view
    #view = ViewFolder(root, controller)
    #view.vol_str = "40%"
    #view.time_to_sleep_str = "00:00"
    #view.title_text = "Hello Worlds"
    #view.img_prime_path = Path(r'D:\Media\Audiobooks\AudiobookPi\Harry Potter 01 - the Philiophers Stone')

    # Create and pack the test view
    view = ViewTrack(root, controller)
    view.title_list = ["1", "odhf", "woeihr", "sjkehrf........................................"]
    view.bold_index = 1
    

    root.mainloop()