import subprocess
import easygui
import notify_sys

def main_actions(command):
    main_cmd = command.pop(0)
    if len(command) == 0:
        return 0
    if main_cmd == "ouvre":
        open_handler(command)
    elif main_cmd == "ferme":
        close_handler(command)
    elif main_cmd == "baisse":
        decrease_handler(command)
    elif main_cmd =="augmente":
        increase_handler(command)


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
    return 0

def decrease_handler(command):
    return 0