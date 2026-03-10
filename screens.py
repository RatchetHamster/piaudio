from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

WIDTH = 240
HEIGHT = 240

class ViewBase:
    def __init__(self, parent, controller):
        self.controller = controller
        self.parent = parent

        # --- Canvas ---
        self.image = Image.new("RGB", (WIDTH, HEIGHT), (200,200,200))
        self.draw = ImageDraw.Draw(self.image)

        # --- Draw Icon Backdrops ---
        self.draw_icons("icon-backdrop", rotation=0, pos="nw")
        self.draw_icons("icon-backdrop", rotation=0, pos="sw")
        self.draw_icons("icon-backdrop", rotation=180, pos="ne")
        self.draw_icons("icon-backdrop", rotation=180, pos="se")

        self.font= ImageFont.load_default()

        self._vol_str = '-- %'
        self._time_to_sleep_str = "--:--"


    # ---------- setters ----------

    @property
    def vol_str(self):
        return self._vol_str

    @vol_str.setter
    def vol_str(self, value):
        self._vol_str = value
        self.render()

    @property
    def time_to_sleep_str(self):
        return self._time_to_sleep_str

    @time_to_sleep_str.setter
    def time_to_sleep_str(self, value):
        self._time_to_sleep_str = value
        self.render()

    # ---------- drawing ----------

    def draw_icons(self, icon_name, rotation, pos, h_pad=47, w_pad=0):

        path = os.path.join("resources", f"{icon_name}.png")

        img = Image.open(path).convert("RGBA")
        img = img.rotate(rotation, expand=True)

        if icon_name != "icon-backdrop":
            alpha = img.getchannel("A")
            white = Image.new("RGBA", img.size, (255, 255, 255))
            img = Image.composite(white, img, alpha)

        if pos == "nw":
            x = w_pad
            y = h_pad
        elif pos == "ne":
            x = WIDTH - img.width - w_pad
            y = h_pad
        elif pos == "sw":
            x = w_pad
            y = HEIGHT - img.height - h_pad
        elif pos == "se":
            x = WIDTH - img.width - w_pad
            y = HEIGHT - img.height - h_pad

        self.image.paste(img, (x, y), img)

    def draw_header(self):

        self.draw.text(
            (WIDTH - 5, 3),
            self._vol_str,
            fill="black",
            anchor="ra",
            font=self.font
        )

        self.draw.text(
            (WIDTH // 2, 3),
            self._time_to_sleep_str,
            fill="black",
            anchor="ma",
            font=self.font
        )

    def render(self):
        frame = self.image.copy()
        draw = ImageDraw.Draw(frame)
        self.draw_header()
        self.parent.hardware.screen.display.display(frame)


class ViewFolder(ViewBase):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # --- Draw Icons ---
        self.draw_icons("icon-time-onoff", rotation=0, pos="nw", h_pad=50, w_pad=3)
        self.draw_icons("icon-rightarrow", rotation=180, pos="sw", h_pad=50, w_pad=3)
        self.draw_icons("icon-list", rotation=0, pos="ne", h_pad=50, w_pad=3)
        self.draw_icons("icon-rightarrow", rotation=0, pos="se", h_pad=50, w_pad=3)

        # --- Default Albumn ---
        img = Image.open(r'/home/pi/piaudio/resources/default_cover.png')
        self.default_art = img.resize((100, 100))
        self.default_art_sm = img.resize((60, 60))

        self._img_prime_path = None
        self._img_prev_path = None
        self._img_next_path = None
        self._title_text = None

    # ---------- setters ----------

    @property
    def img_prime_path(self):
        return self._img_prime_path

    @img_prime_path.setter
    def img_prime_path(self, value):
        self._img_prime_path = value
        self.render()

    @property
    def img_prev_path(self):
        return self._img_prev_path

    @img_prev_path.setter
    def img_prev_path(self, value):
        self._img_prev_path = value
        self.render()

    @property
    def img_next_path(self):
        return self._img_next_path

    @img_next_path.setter
    def img_next_path(self, value):
        self._img_next_path = value
        self.render()

    @property
    def title_text(self):
        return self._title_text

    @title_text.setter
    def title_text(self, value):
        self._title_text = value
        self.render()

    # ---------- render ----------

    def render(self):

        frame = self.image.copy()
        draw = ImageDraw.Draw(frame)

        # images
        prev = self._load_image(self._img_prev_path, (60, 60)) or self.default_art_sm
        prime = self._load_image(self._img_prime_path, (100, 100)) or self.default_art
        nxt = self._load_image(self._img_next_path, (60, 60)) or self.default_art_sm

        frame.paste(prev, (5, 90))
        frame.paste(prime, (70, 70))
        frame.paste(nxt, (WIDTH - 65, 90))

        if self._title_text:
            draw.text(
                (WIDTH // 2, HEIGHT - 60),
                self._title_text,
                fill="black",
                anchor="ma",
                font=self.font
            )

        self.parent.hardware.screen.display.display(frame)

    def _load_image(self, path, size):

        if path is None:
            return None

        path = Path(path) / "cover.jpg"

        if path.exists():
            img = Image.open(path)
            return img.resize(size)

        return None
    

class ViewTrack(ViewBase):

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.draw_icons("icon-time-onoff", 0, "nw", 50, 3)
        self.draw_icons("icon-rightarrow", 270, "sw", 50, 3)
        self.draw_icons("icon-list", 0, "ne", 50, 3)
        self.draw_icons("icon-rightarrow", 90, "se", 50, 3)

        self._title_list = []
        self._bold_index = None

    @property
    def title_list(self):
        return self._title_list

    @title_list.setter
    def title_list(self, value):
        self._title_list = value
        self.render()

    @property
    def bold_index(self):
        return self._bold_index

    @bold_index.setter
    def bold_index(self, value):
        self._bold_index = value
        self.render()

    def render(self):

        frame = self.image.copy()
        draw = ImageDraw.Draw(frame)

        for i in range(8):

            if i >= len(self._title_list):
                break

            y = 35 + i * 25

            if i == self._bold_index:
                draw.rectangle((30, y - 2, 210, y + 20), fill=(180, 200, 200))

            draw.text(
                (35, y),
                self._title_list[i],
                fill="black",
                font=self.font_sm
            )

        self.parent.hardware.screen.display.display(frame)