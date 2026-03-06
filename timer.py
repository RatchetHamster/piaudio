from datetime import datetime, timezone, timedelta

class Timer():
    """ A stand alone timer that allows you to set duration to idle, duration to sleep, and night off times. Any 
    of these can be set to None to make them not count. use 'state' to dertermine if  on, off or idle. Durations
    until these points can also be returned. """

    def __init__(self, # Night trumps sleep, sleep trumps idle
                 idle_time = 5,         # (mins) of inactivity until idle [None will switch idle off]
                 sleep_time = 120,      # (mins) of inactivity until off [None will switch sleep off]
                 night_start = (22,0),  # (hh,m) 24hr format, start time when go off [None will switch night off]
                 night_end = (6,0)):    # (hh,m) 24hr format, end time when go on [None will switch night off]
        self.idle_time = idle_time
        self.sleep_time = sleep_time
        self.night_start = night_start
        self.night_end = night_end

        # self.state = "on", "idle", "off"

        # Last interactions
        self.last_idle_activity = self.now
        self.last_sleep_activity = self.now

    # --- Properties ---
    @property
    def now(self):
        return datetime.now(timezone.utc)
    
    @property
    def state(self):
        if self.is_night(self.now) or self.is_sleep(self.now):
            return "off"
        elif self.is_idle(self.now):
            return "idle"
        else:
            return "on"

    @property
    def time_until_idle(self):
        return self.last_idle_activity + timedelta(minutes=self.idle_time) - self.now if self.idle_time is not None else None

    @property
    def time_until_sleep(self):
        return self.last_sleep_activity + timedelta(minutes=self.sleep_time) - self.now if self.sleep_time is not None else None
    
    @property
    def time_until_night_start(self):
        return self.night_start - self.now if self.night_start is not None else None
    
    @property
    def time_until_night_end(self):
        return self.night_end - self.now if self.night_end is not None else None
    
    @property
    def time_until_off(self):
        if self.time_until_sleep is None and self.time_until_night_start is None:
            return None
        elif self.time_until_sleep is None:
            return self.time_until_night_start
        elif self.time_until_night_start is None:
            return self.time_until_sleep
        else:
            return min(self.time_until_sleep, self.time_until_night_start)

    # --- is logic ---
    def is_night(self, time):
        if None in (self.night_start, self.night_end):
            return None
        
        start = time.replace(hour=self.night_start[0], minute=self.night_start[1], second=0)
        end = time.replace(hour=self.night_end[0], minute=self.night_end[1], second=0)

        # Handle ranges that cross midnight
        if start < end:
            return start <= time < end
        else:
            return time >= start or time < end
    
    def is_sleep(self, time):
        return self.is_past_duration(self.last_sleep_activity, self.sleep_time, time) if self.sleep_time is not None else None
    
    def is_idle(self, time):
        return self.is_past_duration(self.last_idle_activity, self.idle_time, time) if self.idle_time is not None else None
    

    # --- Helpers ---
    def is_past_duration(self, last_activity, dur_mins, time):
        end_time = last_activity + timedelta(minutes=dur_mins)
        return time > end_time
    
    def nudge_idle(self):
        self.last_idle_activity = self.now

    def nudge_sleep(self):
        self.last_sleep_activity = self.now

    def nudge(self):
        self.nudge_idle()
        self.nudge_sleep()
    