import subprocess
import easygui
import notify_sys
import screen_brightness_control as sbc
from grammar import NUMBER_DICT


import pulsectl

pulse_vol = pulsectl.Pulse('volume-control')
pulse_mic = pulsectl.Pulse('mic-control')
# Récupérer le périphérique de sortie par défaut
sink = pulse_vol.sink_list()[0]
source = pulse_mic.source_list()[0]
def volume_set(vol):
    volume = sink.volume
    volume.value_flat = vol
    pulse_vol.volume_set(sink,volume)

def volume_up(step=0.05):  # 5%
    volume = sink.volume
    volume.value_flat = min(1.5, volume.value_flat + step)  # max 150%
    pulse_vol.volume_set(sink, volume)

def volume_down(step=0.05):
    volume = sink.volume
    volume.value_flat = max(0.0, volume.value_flat - step)
    pulse_vol.volume_set(sink, volume)

def mute_toggle():
    pulse_vol.mute(sink, not sink.mute)

def mic_toggle():
    pulse_mic.mute(source,True)
   # pulse_mic.source_suspend(True)



def main_actions(command):
    main_cmd = command.pop(0)
    if len(command) == 0:
        return 0
    if main_cmd in ["ouvre","allume"]:
        open_handler(command)
    elif main_cmd == "ferme":
        close_handler(command)
    elif main_cmd == "baisse":
        decrease_handler(command)
    elif main_cmd =="augmente":
        increase_handler(command)
    elif main_cmd == "verrouille":
        lock_handler(command)


def open_handler(command):
    argument = command[0]
    if argument == "le" or argument == "les":
        argument = command[1]
    if argument == "navigateur":
        subprocess.run(["firefox"])
    elif argument == "terminal":
        subprocess.run(["kitty","--detach","--directory","~"]) 
    elif argument == "fichier" or argument == "document":
        subprocess.run(["thunar"])
    elif argument == "son":
        mute_toggle()
    elif argument == "micro":
        mic_toggle()
    else :
        return


#ps -e |grep -e fir -e chr -e bing -e opera -e brave
def close_handler(command):
    multiple_flag = False
    argument = command[0]
    if argument == "le" :
        argument = command[1]
    if argument == "les": 
        argument = command[1]
        multiple_flag = True


    if argument == "navigateur":
        sub_command = "grep -e'firefox' -e 'chrome' -e 'opera' -e 'brave'"
    elif argument == "terminal" or argument == "terminaux":
        sub_command = "grep -e'kitty' -e 'alacritty' -e 'konsole' -e 'terminator'"
    elif argument =="document" or argument == "fichier":
        sub_command = "grep -e'thunar' -e 'nautilus'"
    elif argument == "toi":
        notify_sys.notifier("","Going to sleep")
        exit(0)
    elif argument == "son":
        mute_toggle()
    elif argument == "micro":
        mic_toggle()
    else:#default case does nothing to prevent crash
        return

    #First fetching processes then removing the ones not in our tty 
    cmd = "ps -e|"+sub_command+"| grep -e tty"
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    processes = str(output).split(" ")
    processes.pop(0)#removing the 'b'
    #removing the '' 
    for i in range(len(processes)):
        if processes.__contains__(''):
            processes.remove('')
        else :
            break

    choices_list=[]
    choices_dict={}
    for i in range(0,len(processes),4):
        process = f"{processes[i]} {processes[i+1]} {processes[i+2]} {processes[i+3].removesuffix("\n")}"
        choices_list.append(process)
        choices_dict[process] = processes[i]

    if len(choices_list) == 0:
        notify_sys.notifier("RAS","Il n'y a pas de " + argument +" en train de tourner")
        return # nothing to do
    elif len(choices_list) == 1 :
        subprocess.run(["kill",choices_dict[choices_list[0]]])
    if multiple_flag == True:
        for key in choices_dict:
            subprocess.run(["kill",choices_dict[key]])
    else :
        msg ="Choose the " + argument + " to kill"
        title = "Killer Queen"
        varp= easygui.choicebox(msg=msg,title=title,choices=choices_list)
        if varp is not None:
            subprocess.run(["kill",choices_dict[varp]])


def increase_handler(command):
    argument = command.pop(0)
    if argument in [ "le","l","les"] and len(command) >0:
        argument = command.pop(0)

    dest_number = 10
    flag_add = True
    if len(command) > 1 : #it means there are additionnal infos
        dest_number = NUMBER_DICT[command[1]]
        if command[0] in [ "a","jusqu'a"] :
            flag_add = False
        if command[0] == "de":
            flag_add = True 
    if argument == "lumiere":
        curr_bright = sbc.get_brightness()[0]
        if flag_add :
            sbc.fade_brightness(curr_bright+dest_number,start=curr_bright,interval=0.1)
        if dest_number >= curr_bright and not flag_add:
            sbc.fade_brightness(dest_number,start=curr_bright,interval=0.1)

    if argument in ["volume","son"]:
        if flag_add:
            volume_up(0.1)
        if sink.volume.value_flat <= dest_number/100.0 and not flag_add:
            volume_set(dest_number/100.0) 

            


def decrease_handler(command):
    argument = command.pop(0)
    if argument in [ "le","l","les"] and len(command) >0:
        argument = command.pop(0)


    dest_number = 10
    flag_sub = True
    if len(command) > 1 : #it means there are additionnal infos
        dest_number = NUMBER_DICT[command[1]]
        if command[0] in [ "a","jusqu'a"] :
            flag_sub = False
        if command[0] == "de":
            flag_sub = True 

    if argument == "lumiere":
        curr_bright = sbc.get_brightness()[0]
        if flag_sub :
            sbc.fade_brightness(curr_bright-dest_number,start=curr_bright,interval=0.1)
        if dest_number >= curr_bright and not flag_sub:
            sbc.fade_brightness(dest_number,start=curr_bright,interval=0.1)

    if argument in ["volume","son"]:
        if flag_sub:
            volume_down(0.1)
        if sink.volume.value_flat >= dest_number/100.0 and not flag_sub:
            volume_set(dest_number/100.0) 


def lock_handler(command):
    argument = command[0]
    
    if argument in [ "le","l","les"] and len(command) >1:
        argument = command[1]
    if argument in ["ordinateur","pc"]:
        subprocess.run(["lock"]) # ATTENTION => C'est une commande perso, changez pour que ça corresponde à votre système 