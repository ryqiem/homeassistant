import appdaemon.appapi as appapi
import circadian_gen
import time
import datetime

#
# Carpediem app
#
# Args:
#   switch: The switch that initializes the script
#   factor: the input_select that determines the factor length

class MovieMode(appapi.AppDaemon):

    def initialize(self):
        self.log("Initializing {} with switch: {}".format(__name__, self.args["switch"]))

        #Setup the switch object
        switch = self.args["switch"]

        #Register callback for switch turning on
        self.listen_state(self.on, switch, new = "on")
        self.listen_state(self.off, switch, new = "off")

    def on(self, entity, attribute, old, new, kwargs):
        #Initiating circadin
        self.log("Moviemode on!")
        self.turn_off("input_boolean.circadian") #Turn off circadian temporarily
        if self.get_state("media_player.pioneer") == "off":
            self.turn_on("media_player.pioneer")
            i = 0
            while (i < 15) and self.get_state("media_player.pioneer") == "off":
                time.sleep(1)
                i += 1
                self.log("Receiver is off, checking in 1 second, i = {}".format(i))
        elif self.get_state("media_player.pioneer") == "on":
            self.log("Receiver is already on, proceding")

        self.setstate("light.monitor", self.global_vars["c_brightness"] * 0.5, 10)
        self.setstate("light.loft", 0, 8)
        self.setstate("light.reol", self.global_vars["c_brightness"] * 0.2, 13)

        #self.turn_on("script.moviemode")

        self.turn_on("switch.benq")
        if self.get_state("media_player.pioneer", "source") != "TUNER":
            i = 0
            while (i < 30) and self.get_state("media_player.pioneer", "source") != "TUNER":
                self.call_service("media_player/select_source", entity_id = "media_player.pioneer", source = "TUNER")
                i += 1
                time.sleep(1)
                self.log("Source is not TUNER, trying again")
        else:
            self.log("Source is already tuner")

        self.call_service("media_player/volume_set", entity_id = "media_player.pioneer", volume_level = 0.8)
        time.sleep(2)
        self.call_service("media_player/select_source", entity_id = "media_player.pioneer", source = "RPI")

        if self.get_state("media_player.pioneer", "source") != "RPI" and self.get_state("media_player.pioneer", "source") == "TUNER":
            i = 0
            while (i < 10) and self.get_state("media_player.pioneer", "source") != "RPI":
                self.call_service("media_player/select_source", entity_id = "media_player.pioneer", source = "RPI")
                i += 1
                time.sleep(1)
        else:
            self.log("Source is already RPI")
        self.call_service("media_player/volume_set", entity_id = "media_player.pioneer", volume_level = 0.7)

        self.turn_off("light.loft")
        self.turn_off("light.hallway")

    def off(self, entity, attribute, old, new, kwargs):
        self.setstate("light.monitor", self.global_vars["c_brightness"], 80, self.global_vars["c_colortemp"])
        self.setstate("light.reol", self.global_vars["c_brightness"], 80, self.global_vars["c_colortemp"])
        self.setstate("light.loft", self.global_vars["c_brightness"], 80, self.global_vars["c_colortemp"])

        vollevel = self.get_state("media_player.pioneer", "volume_level")

        i = 0
        while (i<10):
            vollevel -= (0.005 * i)
            self.call_service("media_player/volume_set", entity_id = "media_player.pioneer", volume_level = vollevel)
            time.sleep(2)
            i += 1

        self.turn_off("switch.benq")
        self.turn_off("media_player.pioneer")
        self.turn_on("input_boolean.circadian") #Turn circadian adjustments back on
        self.log("Moviemode off!")
        self.call_service("media_player/media_stop", entity_id = "media_player.rasplex")

    def setstate(self, lt, bness, fade, color=""):
        self.modulator = 1
        switch = self.args["switch"]

        self.log("Set " + lt + " to fade in " + str(fade * self.modulator) + "s")

        if color != "":
            self.turn_on(lt, brightness = bness, transition = self.modulator * fade, xy_color = color)
        else:
            self.turn_on(lt, brightness = bness, transition = self.modulator * fade)
