import appdaemon.appapi as appapi
import time
import datetime

#
# Carpediem app
#
# Args:
#   switch: The switch that initializes the script
#   light: The light that's used for sunrise

class Sunrise(appapi.AppDaemon):

    def initialize(self):
        self.log("Initializing sunrise")

        #Setup the switch object
        switch = self.args["switch"]

        #Reset the switch at 6:25 each day
        time = datetime.time(6, 25, 0)
        self.run_daily(self.rise, time)

    def rise(self, entity="", attribute="", old="", new="", kwargs=""):
        #Make short corner light var
        self.modulator = 1
        self.turn_off("input_boolean.circadian")
        self.setstate("light.monitor", 100, 1200, [ 0.674, 0.322 ])
        self.turn_on("input_boolean.circadian")

    def setstate(self, lt, bness, fade, color=""):
        switch = self.args["switch"]

        if self.get_state(switch) == "on":
            self.log("Set " + lt + " to fade in " + str(fade * self.modulator) + "s")

            if color != "":
                self.turn_on(lt, brightness = bness, transition = self.modulator * fade, xy_color = color)
            else:
                self.turn_on(lt, brightness = bness, transition = self.modulator * fade)


            time.sleep(self.modulator * fade)
        else:
            self.log("Switch turned off, terminating")
