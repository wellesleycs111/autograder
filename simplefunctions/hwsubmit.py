"""Homework submission script to tempest for CS111.
"""

__author__='Sravana Reddy'

from paramiko import Transport, SFTPClient
import os
import Tkinter as tk

# hardcode problem set ID and list of files to submit
ps = 'ps03'
filelist = ['rock_paper_scissors.py', 'wordprops.py', 'logs']

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
    for itemname in filelist:
        print 'uploading', itemname
        if os.path.isdir(itemname):
            try:
                sftpclient.chdir(os.path.join(userdrop, ps, itemname))
            except:
                sftpclient.mkdir(os.path.join(userdrop, ps, itemname))
                sftpclient.chdir(os.path.join(userdrop, ps, itemname))
            for filename in os.listdir(itemname):
                sftpclient.put(os.path.join(itemname, filename), filename)
            sftpclient.chdir('..')
        else:
            sftpclient.put(itemname, itemname)

    sftpclient.close()
    trans.close()
    print 'Success!'

def checkfiles():
    """check for missing files"""
    for itemname in filelist:
        if not os.path.exists(itemname):
            print itemname, 'does not exist'
            print 'Check your folder and try again.'
            return False
    return True

if __name__=='__main__':
    if checkfiles():
        client = Prompt()
        client.mainloop()
