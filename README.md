# Falcon-Punch
force reinstall and remediation of broken Crowdstrike Falcon agents on macOS


## What is this?

This is a script you can use to forceibly remove Crowdstrike Falcon from a macOS system. 

## Why are you doing this?

There are edge cases where the built in maintenance mechanims with in Crowdstrike will fail.  They are mostly edge cases, however, there is no good remediation with automation that the vendor can supply.  Your choices are boot into Safe Boot or Recovery Mode and manually remove these components, which does not scale at all.  This is meant to be a one off type of solution, not an actual solution

## Use at your own risk

I have tested this on macOS 10.14.6 and 10.15.3.  Also tested this with Falcon Sensor versions 4.x and 5.x for macOS.  I have only used this on systems that are broken beyond repair and do not work with the built in maintenance token mechanism Crowdstrike provides.

## Requiremetns:

Python 3.4+

jamf pro

## workflow

The workflow is not too complicated.  It starts with logical checks via scripts you can execute on endpoints.  There are tons of edge cases and false positives you can get, but I have narrowed down my usecase to `/Library/CS/falconctl` and `sysctl cs` having valid `stdout` output and an exit code of `0`.  If those conditions are not met I assume the agent is broken, and will flag it for this workflow.  The other check I am doing is the version (`sysctl -n cs.version`) and tracking any client that is not auto updating from the cloud tenant.  This is obviously, only applicable if you have enabled cloud updates.   

When the `falcon_punch.py` script runs successfully it will drop a receipt file (`cs.txt`) that is tracked via jamf pro EA and criteria for a smart group.  I chose this method to keep all the logic in the code and not in the smart group logic server side.  Once the code runs and blasts Crowdstrike Falcon off the file system, it will drop this text file and calculate smart group membership based off of that file existing

When the next checkin occurs after after the reboot, a policy will execute the installation of the Falcon Sensor and will register it with the post install script.  I will try to upload screen shots to make this more visual at a later date

## Could this be improved?

Absolutely, I could write the code to accept arguments, or funble around with date-time libs to convert readable human date stamps to epoch date stamps.  However, my main goal is to not use this, except in situations where the built in mechanisms fail.  I intend to use the built in maitnenance mechanism with Crowdstrike once I remeidate all the broken agents from various edge cases.
