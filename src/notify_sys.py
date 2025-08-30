from notifypy import Notify
import os
from time import sleep

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "robot.png")

def notifier(title,message):
    notification = Notify()
    notification.title = "Jarvis " + title
    notification.message = message
    notification.icon = filename
    notification.send()
    sleep(2)