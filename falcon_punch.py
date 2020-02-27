#!/opt/snowflake/bin/python3

"""
script to prompt user and force reboot the system to remove CS and reinstall at reboot
this will require a dummy file and a recon to flag systems in scope of this policy

REQUIREMENTS:
Python 3.4+
Jamf Pro server

credits:

Inspired by Patrick Gallagher from Mac Admin Slack as this code was based off their original script
"""

# import modules

import subprocess
import os
import sys
import shutil
from pathlib import Path
import time

# global vars

# current epoch time stamp
TIME_NOW = time.time()
# target date before we force install/reboot
# set the epoch date stamp of when you want enforcement to start
TARGET_DATE = "replace this with epoch time stamp"
# Get days left
DAYS_LEFT = int(round((TARGET_DATE - TIME_NOW) / 84600))
# heart symbol for that love from IT
SYMBOL = u"\u2764\ufe0f"
# custom icon path for branding on jamf helper dialog boxes
ICON = ""
# receipt file path, name it cs.txt - ex: /Library/Application Support/JAMF/cs.txt
RFILE_PATH = ""
# message to prompt the user to quit and update an app
MESSAGE = """Greetings:

IT would like to reboot your computer to install a security update.  Please click on the "Restart Now" button to continue, 
this will force your computer to restart immediately.  Please save all your work before hitting the "Restart Now," button.

You may click "Cancel" to delay this update, but it will be enforced in {1} days

{0} IT
""".format(
    SYMBOL, DAYS_LEFT
)


FORCE_MSG = """Greetings:

This device has exceeded the remaining allowed time for installing the security updates and restarting.  This device will be
forced to restart and apply the update in 60 seconds.  Please save and exit all your work now.

{0} IT""".format(
    SYMBOL
)


# start functions


def prompt_user(prompt):
    """simple jamf helper dialog box"""
    # test to see what icons are available on the file system from global var
    icon = ICON
    if not os.path.exists(icon):
        # default fail over icon in case our custom one does not exist
        icon = "/System/Library/CoreServices/Problem Reporter.app/Contents/Resources/ProblemReporter.icns"
        # build the jamf helper unix command in a list
    cmd = [
        "/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper",
        "-windowType",
        "utility",
        "-title",
        "Quit Applications",
        "-description",
        prompt,
        "-icon",
        icon,
        "-button1",
        "Restart",
        "-button2",
        "Cancel",
        "-defaultbutton",
        "1",
    ]
    # call the command via subprocess
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # get stdout and stderr
    out, err = proc.communicate()
    # check for exit status for button clicked, 0 = OK 2 = Cancel
    if proc.returncode == 0:
        # user clicked OK
        return True
    if proc.returncode == 2:
        # user clicked cancel
        return False
    # if there is any other return print it
    else:
        print("Error: %s" % err)


def force_prompt(prompt):
    """simple jamf helper dialog box"""
    # pass global var
    icon = ICON
    # test to see what icons are available on the file system
    if not os.path.exists(icon):
        # default fail over icon in case our custom one does not exist
        icon = "/System/Library/CoreServices/Problem Reporter.app/Contents/Resources/ProblemReporter.icns"
        # build the jamf helper unix command in a list
    cmd = [
        "/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper",
        "-windowType",
        "utility",
        "-title",
        "Quit Applications",
        "-description",
        prompt,
        "-icon",
        icon,
        "-button1",
        "Restart",
        "-defaultbutton",
        "1",
        "-timeout",
        "60",
        "-countdown",
        "-alignCountdown",
        "center",
    ]
    # call the command via subprocess
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # get stdout and stderr
    out, err = proc.communicate()
    # check for exit status for button clicked, 0 = OK 2 = Cancel
    if proc.returncode == 0:
        # user clicked OK
        return True
    if proc.returncode == 2:
        # user clicked cancel
        return False
    # if there is any other return print it
    else:
        print("Error: %s" % err)


def unload_daemons():
    """simple function to unload CS daemons"""
    daemons = [
        "/Library/LaunchDaemons/com.crowdstrike.falcond.plist",
        "/Library/LaunchDaemons/com.crowdstrike.userdaemon.plist",
    ]
    for daemon in daemons:
        subprocess.run(["/bin/launchctl", "unload", daemon])
    # now kill the processes
    procs = ["falcond", "CSDaemon"]
    for proc in procs:
        cmd = ["/usr/bin/killall", "-9", proc]
        subprocess.run(cmd)


def unload_kext():
    """unload the CS kext"""
    cmd = ["/sbin/kextunload", "-b", "/Library/CS/kexts/Agent.kext"]
    subprocess.run(cmd)


def delete_cs_folders():
    """delete CS files an folders"""
    files = [
        "/Library/LaunchDaemons/com.crowdstrike.userdaemon.plist",
        "/Library/LaunchDaemons/com.crowdstrike.falcond.plist",
    ]
    folders = "/Library/CS"
    # delete the daemons
    for f in files:
        os.remove(f)
    # delete the folders
    shutil.rmtree(folders)


def run_receipt():
    """drop a file and force a jamf recon to place it in the smart group to install CS after a reboot"""
    # receipt file path
    rfile = RFILE_PATH
    Path(rfile).touch()
    cmd = ["/usr/local/bin/jamf", "recon"]
    subprocess.run(cmd)


def force_reboot():
    """rebooting client system"""
    cmd = ["/sbin/shutdown", "-r", "NOW"]
    subprocess.run(cmd)


def main():
    """gotta get some main"""
    # check if there are zero days left
    if DAYS_LEFT == 0:
        force_prompt(FORCE_MSG)
        time.sleep(60)
        unload_daemons()
        unload_kext()
        delete_cs_folders()
        run_receipt()
        force_reboot()
        sys.exit(0)
    # if there are days remaining prompt
    if prompt_user(MESSAGE):
        unload_daemons()
        unload_kext()
        delete_cs_folders()
        run_receipt()
        force_reboot()
    else:
        # user clicked not now
        sys.exit(0)


if __name__ == "__main__":
    main()
