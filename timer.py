from datetime import datetime, timedelta


class Timer:
    """Handles idle, sleep and night shutoff logic."""

    def __init__(
        self,
        idle_time=5,        # minutes until idle
        sleep_time=120,     # minutes until off
        night_start=(22, 0),
        night_end=(6, 0)):
        
        self.idle_time = idle_time
        self.sleep_time = sleep_time
        self.night_start = night_start
        self.night_end = night_end

        now = datetime.now()
        self.last_idle = now
        self.last_sleep = now

    # ------------------------
    # Core helpers
    # ------------------------

    @property
    def now(self):
        return datetime.now()

    def _duration_passed(self, last, minutes):
        if minutes is None:
            return False
        return self.now >= last + timedelta(minutes=minutes)

    # ------------------------
    # State logic
    # ------------------------

    def is_idle(self):
        return self._duration_passed(self.last_idle, self.idle_time)

    def is_sleep(self):
        return self._duration_passed(self.last_sleep, self.sleep_time)

    def is_night(self):
        if None in (self.night_start, self.night_end):
            return False

        now = self.now
        start = now.replace(hour=self.night_start[0], minute=self.night_start[1], second=0, microsecond=0)
        end = now.replace(hour=self.night_end[0], minute=self.night_end[1], second=0, microsecond=0)

        if start < end:
            return start <= now < end
        else:  # crosses midnight
            return now >= start or now < end

    @property
    def state(self):
        if self.is_night() or self.is_sleep():
            return "off"
        if self.is_idle():
            return "idle"
        return "on"
    

    @property
    def time_until_off(self):
        """Return time until screen turns off (sleep or night) as 'HH:MM'."""

        times = []

        now = self.now

        # Sleep timeout
        if self.sleep_time is not None:
            sleep_end = self.last_sleep + timedelta(minutes=self.sleep_time)
            times.append(sleep_end - now)

        # Night start
        if self.night_start is not None:
            night = now.replace(
                hour=self.night_start[0],
                minute=self.night_start[1],
                second=0,
                microsecond=0
            )

            if night <= now:
                night += timedelta(days=1)

            times.append(night - now)

        if not times:
            return None

        t = min(times)

        if t.total_seconds() <= 0:
            return "00:00"

        total_minutes = int(t.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60

        return f"{hours:02}:{minutes:02}"

    # ------------------------
    # Activity nudges
    # ------------------------

    def nudge_idle(self):
        self.last_idle = self.now

    def nudge_sleep(self):
        self.last_sleep = self.now

    def nudge(self):
        now = self.now
        self.last_idle = now
        self.last_sleep = now