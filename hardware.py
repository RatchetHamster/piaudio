from gpiozero import PWMLED, Button
from ST7789 import ST7789

# Button A is TL
# Button B is BL
# Button X is TR
# Button Y is BR

class Screen():
    def __init__(self):
        
        self.DISPLAY_W = 240
        self.DISPLAY_H = 240

        self.display = ST7789(
            rotation=90,
            port=0,
            cs=1,
            dc=9,
            backlight=None, #Modified as we will control this on shutdown
            spi_speed_hz=80 * 1000 * 1000)

        # Backlight:
        self.backlight = PWMLED("BCM13", frequency=500)
        self.screen_on()
        self._state = "on"  #"on", "off", "idle"
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        if value != self.state:
            self._state = value
            if self.state == "off":
                self.screen_off()
            elif self.state == "idle":
                self.screen_dim()
            else: #on
                self.screen_on()

    def screen_on(self):
        self.backlight.value = 1.0 # start at 100%

    def screen_off(self):
        self.backlight.value = 0.0 # start at 0%

    def screen_dim(self):
        self.backlight.value = 0.2 # start at 20%


class Board_Button():
    def __init__(self, pin, label, press_fun_name=None, held_fun_name=None, release_fun_name=None, hold_time=0.7, hold_repeat=True):
        self.label = label
        self.press_fun_name = press_fun_name
        self.held_fun_name = held_fun_name
        self.release_fun_name = release_fun_name

        self.button = Button(pin, pull_up=True, hold_time=hold_time, hold_repeat=hold_repeat)

        self.button.when_pressed = self.pressed
        self.button.when_held = self.held
        self.button.when_released = self.released

        self.was_held = False

    def pressed(self):
        self.was_held = False
        if self.press_fun_name:
            self.press_fun_name()

    def held(self):
        self.was_held = True
        if self.held_fun_name:
            self.held_fun_name()

    def released(self):
        if not self.was_held:
            if self.release_fun_name:
                self.release_fun_name()
        self.was_held = False


class HardwareController():
    def __init__(self,
                 Ashort_fun, 
                 Bshort_fun,
                 Xshort_fun,
                 Yshort_fun,
                 Along_fun, 
                 Blong_fun,
                 Xlong_fun, 
                 Ylong_fun):
        
        # --- Buttons ---
        self.buttons = [
            Board_Button(5, 'A', press_fun_name=self.but_press, held_fun_name=Along_fun, release_fun_name=Ashort_fun),
            Board_Button(6, 'B', press_fun_name=self.but_press, held_fun_name=Blong_fun, release_fun_name=Bshort_fun),
            Board_Button(16,'X', press_fun_name=self.but_press, held_fun_name=Xlong_fun, release_fun_name=Xshort_fun),
            Board_Button(24,'Y', press_fun_name=self.but_press, held_fun_name=Ylong_fun, release_fun_name=Yshort_fun)]

        # --- Att ---
        self.screen = Screen()
        
    def but_press(self):
        pass
