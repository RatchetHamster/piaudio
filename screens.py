from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

WIDTH = 240
HEIGHT = 240

class ViewBase:
    def __init__(self, parent, controller):
        self.controller = controller
        self.parent = parent

        self.image = Image.new("RGB", (WIDTH, HEIGHT), (200,200,200))
        self.draw = ImageDraw.Draw(self.image)

        self.draw_icons("icon-backdrop", rotation=0, pos="nw")
        self.draw_icons("icon-backdrop", rotation=0, pos="sw")
        self.draw_icons("icon-backdrop", rotation=180, pos="ne")
        self.draw_icons("icon-backdrop", rotation=180, pos="se")

        self.font = ImageFont.truetype(r'/home/pi/piaudio/resources/Inter-Regular.otf', 24)
        self.font_sm = ImageFont.truetype(r'/home/pi/piaudio/resources/Inter-Regular.otf', 18)
        self.font_bold = ImageFont.truetype(r'/home/pi/piaudio/resources/Inter-Bold.otf', 24)
        self.font_sm_bold = ImageFont.truetype(r'/home/pi/piaudio/resources/Inter-Bold.otf', 18)

        self.vol_str = '-- %'
        self.time_to_sleep_str = "--:--"
        self.frame = self.image.copy()

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
            self.vol_str,
            fill="black",
            anchor="ra",
            font=self.font
        )

        self.draw.text(
            (WIDTH // 2, 3),
            self.time_to_sleep_str,
            fill="black",
            anchor="ma",
            font=self.font
        )


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

        self.img_prime_path = None
        self.img_prev_path = None
        self.img_next_path = None
        self.title_text = None

    # ---------- render ----------

    def render(self):

        self.frame = self.image.copy()
        draw = ImageDraw.Draw(self.frame)

        # images
        prev = self._load_image(self.img_prev_path, (60, 60)) or self.default_art_sm
        prime = self._load_image(self.img_prime_path, (100, 100)) or self.default_art
        nxt = self._load_image(self.img_next_path, (60, 60)) or self.default_art_sm

        self.frame.paste(prev, (5, 90))
        self.frame.paste(prime, (70, 70))
        self.frame.paste(nxt, (WIDTH - 65, 90))

        if self.title_text:
            draw.text(
                (WIDTH // 2, HEIGHT - 60),
                self.title_text,
                fill="black",
                anchor="ma",
                font=self.font)


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

        self.title_list = []
        self.bold_index = None


    def render(self):

        self.frame = self.image.copy()
        draw = ImageDraw.Draw(self.frame)

        for i in range(8):
            if i >= len(self.title_list):
                break
            y = 35 + i * 25

            if i == self.bold_index:
                draw.rectangle((30, y - 2, 210, y + 20), fill=(180, 200, 200))

            draw.text(
                (35, y),
                self.title_list[i],
                fill="black",
                font=self.font)