#!/bin/zsh

# check if cs.txt exists for reboot flow in path you have stored it

file_path=""
if [[ -f "${file_path}" ]]
    then echo "<result>true</result>"
    else echo "<result>false</result>"
fi