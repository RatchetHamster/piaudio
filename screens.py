from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os
from player import CoreMixer

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

        self.font = ImageFont.truetype(r'/home/pi/piaudio/resources/Inter-Regular.otf', 16)
        self.font_sm = ImageFont.truetype(r'/home/pi/piaudio/resources/Inter-Regular.otf', 12)
        self.font_bold = ImageFont.truetype(r'/home/pi/piaudio/resources/Inter-Bold.otf', 16)
        self.font_sm_bold = ImageFont.truetype(r'/home/pi/piaudio/resources/Inter-Bold.otf', 12)

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

        # Header
        vol = CoreMixer().get_vol()
        draw.text(
            (WIDTH - 5, 5),
            f"{vol*100:.0f}%",
            fill="black",
            anchor="rt",
            font=self.font)
        
        time_to_off = self.controller.timer.time_until_off
        time_str = time_to_off if time_to_off is not None else "--:--"
        
        draw.text(
            (WIDTH // 2, 5),
            time_str,
            fill="black",
            anchor="mt",   # middle-top anchor
            font=self.font)

        # images
        prev = self._load_image(self.img_prev_path, (60, 60)) or self.default_art_sm
        prime = self._load_image(self.img_prime_path, (100, 100)) or self.default_art
        nxt = self._load_image(self.img_next_path, (60, 60)) or self.default_art_sm

        self.frame.paste(prev, (5, 90))
        self.frame.paste(prime, (70, 70))
        self.frame.paste(nxt, (WIDTH - 65, 90))

        if self.title_text:
            text = self.title_text

            # Wrap text at 20 characters
            lines = []
            while len(text) > 20:
                split_pos = text.rfind(" ", 0, 20)
                if split_pos == -1:
                    split_pos = 20
                lines.append(text[:split_pos])
                text = text[split_pos:].strip()

            lines.append(text)

            wrapped_text = "\n".join(lines)

            draw.multiline_text(
                (WIDTH // 2, HEIGHT - 60),
                wrapped_text,
                fill="black",
                anchor="ma",
                font=self.font,
                align="center"
            )


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
        self.draw_icons("icon-rightarrow", 90, "sw", 50, 3)
        self.draw_icons("icon-list", 0, "ne", 50, 3)
        self.draw_icons("icon-rightarrow", 270, "se", 50, 3)

        self.title_list = []
        self.bold_index = None


    def render(self):

        self.frame = self.image.copy()
        draw = ImageDraw.Draw(self.frame)

        # Header
        vol = CoreMixer().get_vol()
        draw.text(
            (WIDTH - 5, 5),
            f"{vol*100:.0f}%",
            fill="black",
            anchor="rt",
            font=self.font)

        for i in range(8):
            if i >= len(self.title_list):
                break
            y = 35 + i * 25

            if i == self.bold_index:
                draw.rectangle((30, y - 2, 210, y + 20), fill=(180, 200, 200))
            if self.controller.player.playing_track is not None and self.title_list[i] == self.controller.player.playing_track.name:
                draw.text(
                    (35, y),
                    self.title_list[i],
                    fill="black",
                    font=self.font_bold)
            else:
                draw.text(
                    (35, y),
                    self.title_list[i],
                    fill="black",
                    font=self.font)