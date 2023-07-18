# UT363BT_IFTTT
BT porting over RPi of UT363BT with IFTTTT

Requires to IFTTT triggers:
https://maker.ifttt.com/trigger/winddisconnect handling any disconnection notification
https://maker.ifttt.com/trigger/wind handling wind speed notification

Current speed limit is hard coded as 4.5m/s per line
                                        if (self.windSpeed > 4.5):
