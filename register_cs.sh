#!/bin/zsh

# register the CS agent to our tenant post install
# configure this to intsall as a post install script in a jamf policy
# add your CCID from the Falcon web tenant as a positional parameter

CCID="${4}"

/Library/CS/falconctl license "${CCID}"
/LibraryCS/falconctl load