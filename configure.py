#!/usr/bin/python

# 
# Script to configure and build the Notify plug-in for the Virtual Planner.
#

import sys
import os

# Values and stuff.
path = './notify/notify.py'
line_notify = '        self.path = '
line_username = '        username = '
line_password = '        password = '

# Open the source file.
try:
    notify = open(path, 'r')
    lines = notify.readlines()
    notify.close()
except IOError:
    print "Cannot open notification source file."
    sys.exit(0)

# Get details from the user.
print "Please note that if you want this plug-in to be automagically installed in to Trac's directory, you *must* have write permission to that directory (typically '/usr/share/trac/plugins/'). If you do not, the final part of the build process will fail. See the documentation for more info."
notification_url = raw_input("Please input the address of the 'notification target': ")
auth_username = raw_input("Please enter the user name to access the notification target: ")
auth_password = raw_input("Please enter the password to access the notification target: ")
print ""

if notification_url.strip() == '':
    print "You must enter the address of your Virtual Planner's notification target."
    sys.exit(0)
else:
    line_notify += "'%s'\n" % notification_url

if auth_username.strip() != '':
    line_username += "'%s'\n" % auth_username
    line_password += "'%s'\n" % auth_password

# Update the code.
total_lines = len(lines)
for i in range(0, total_lines):
    if lines[i].strip()[0:9] == 'self.path':
        lines[i] = line_notify
        continue
    if lines[i].strip()[0:10] == 'username =':
        lines[i] = line_username
        lines[(i + 1)] = line_password
        continue

# Write changes to the file.
try:
    notify = open(path, 'w')
    notify.writelines(lines)
except IOError:
    print "Could not write to source file at '" + path + "'. Please check that you have write permission to the file and try again."
    sys.exit(0)

# Run the script to build the plug-in.
print "Plug-in configured, building the egg..."
data = os.system('./build.sh')
print ""
print "All done (unless you saw errors from the build process)."
