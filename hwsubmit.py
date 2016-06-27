"""Homework submission script to tempest for CS111.
"""

__author__='Sravana Reddy'

from paramiko import Transport, SFTPClient
import os
import Tkinter as tk
import time

# hardcode problem set ID and list of files to submit
filelist = ['rock_paper_scissors.py', 'wordprops.py']
dirlist = ['logs']

class Prompt(tk.Tk):
    """a small Tkinter window prompting for username and password"""
    def __init__(self):
        tk.Tk.__init__(self)

        self.title('Authenticate')

        self.user_label = tk.Label(self, text='Enter your tempest username: ')
        self.user_entry = tk.Entry(self)
        self.user_entry.focus()

        self.pw_label = tk.Label(self, text='Enter your password: ')
        self.pw_entry = tk.Entry(self, show="*")

        self.sub = tk.Button(self, text="Submit", command=lambda : connect(self))

        self.user_label.pack()
        self.user_entry.pack()
        self.pw_label.pack()
        self.pw_entry.pack()
        self.sub.pack()

        self.attributes("-topmost", True)  # bring to front of screen

def connect(window):
    ps = open('psid.txt').read().strip()
    username = window.user_entry.get()
    password = window.pw_entry.get()

    window.destroy()

    trans = Transport(('cs.wellesley.edu', 22))
    try:
        trans.connect(username=username, password=password)
        sftpclient = SFTPClient.from_transport(trans)
        print "Connection made... submitting files."
    except:
        print "Connection failed. Check your username and password and try again."
        return

    userdrop = os.path.join('/home', username, 'cs111', 'drop')
    # first create ps directory
    try:
        sftpclient.chdir(os.path.join(userdrop, ps))
    except:
        sftpclient.mkdir(os.path.join(userdrop, ps))
        sftpclient.chdir(os.path.join(userdrop, ps))

    timestamp = '-'.join(map(str, time.localtime()[1:6]))
    sftpclient.mkdir(timestamp)  # for archiving

    for filename in filelist:
        print 'uploading', filename
        sftpclient.put(filename, filename)
        sftpclient.put(filename, os.path.join(timestamp, filename))

    for dirname in dirlist: # TODO: Do directories need to be archived?
        print 'uploading', dirname
        try:
            sftpclient.chdir(dirname)
        except:
            sftpclient.mkdir(dirname)
            sftpclient.chdir(dirname)
        for filename in os.listdir(dirname):
            sftpclient.put(os.path.join(dirname, filename), filename)
        sftpclient.chdir('..')

    """
    sshclient = trans.open_channel("session")
    sshclient.exec_command('ls')
    stdout = []

    while True:
        if sshclient.recv_ready():
            stdout.append(sshclient.recv(4096))
        if sshclient.exit_status_ready():
            break

    print ''.join(stdout)
    """

    sftpclient.close()
    trans.close()
    print 'Success!'

def checkfiles():
    """check for missing files"""
    for itemname in filelist+dirlist+['psid.txt']:
        if not os.path.exists(itemname):
            if itemname.startswith('logs'):
                print "You must run the autograder at least once before submitting. Do not delete the log files."
            else:
                print 'The required', itemname, 'does not exist'
                print 'Check your folder, ensure you are submitting from the correct location, and try again.'
            return False
    return True

if __name__=='__main__':
    if checkfiles():
        client = Prompt()
        client.mainloop()
