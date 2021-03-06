#!/usr/bin/python3

import sys
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QPushButton,
							QHBoxLayout, QVBoxLayout, QPlainTextEdit)
from PyQt5.QtCore import (Qt, QProcess)
from PyQt5.QtGui import (QIcon, QPalette)
from optparse import OptionParser

from pathlib import Path

from update_worker import update_worker_t
from upgrader2 import DialogUpg
import subprocess

class Dialog(QWidget):
    def __init__(self, upgrades, security_upgrades, packages, reboot_required, upg_path):
        QWidget.__init__(self)
        self.upgrades = upgrades
        self.security_upgrades = security_upgrades
        self.upg_path = upg_path
        self.packages = packages

        self.initUI()
        self.upgradeBtn.clicked.connect(self.call_upgrade)
        self.closeBtn.clicked.connect(self.call_reject)

    def initUI(self):
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignHCenter)
        self.upgradeBtn = QPushButton("Upgrade")
        self.closeBtn = QPushButton("Close")
        self.plainTextEdit = QPlainTextEdit()
        text = ""
        self.plainTextEdit.setVisible(False)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setEnabled(False)
        palette = self.plainTextEdit.palette()
        palette.setColor(QPalette.Base, Qt.black)
        palette.setColor(QPalette.Text, Qt.gray)
        self.plainTextEdit.setPalette(palette)


        hbox=QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.upgradeBtn)
        hbox.addWidget(self.closeBtn)
        hbox.addStretch(1)

        vbox=QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.plainTextEdit)
        vbox.addLayout(hbox)

        if self.upg_path == None:
            self.upgradeBtn.setVisible(False)

        self.setLayout(vbox)
        self.setGeometry(300, 300, 500, 150)
        self.setWindowTitle("Update Notifier")
        self.center()

        if self.upgrades > 0:
            text = "There are(is) %s upgrade(s) available and %s security update(s) available" % (self.upgrades, self.security_upgrades)
            self.plainTextEdit.setVisible(True)
            for pkg in self.packages:
                self.plainTextEdit.appendPlainText(str(pkg))

        if reboot_required:
            if text == "":
                text = "Reboot is needed"
                self.upgradeBtn.setVisible(False)
            else:
                text = text + "\nReboot is needed"

        self.label.setText(text)
        self.plainTextEdit.setEnabled(True)

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())self.transaction = self.apt_client.commit_packages(install=installs, remove=removals, reinstall=[], purge=[], upgrade=[], downgrade=[])

    def call_reject(self):
        app.quit()

    def call_upgrade(self):
        self.label.setText("Upgrading....")
        #TODO maybe open another thread so notifier won't freeze
        #process = subprocess.Popen(self.upg_path)
        #process = subprocess.Popen(cmd)
        #process = subprocess.Popen(cmd, shell=True)

        dialogUpg = DialogUpg(options=None, pkg=self.packages)
        dialogUpg.show()

        '''cmd = ['lxqt-sudo', self.upg_path]
        process = subprocess.Popen(cmd)
        process.wait()
        app.quit()'''

class App(QApplication):
    def __init__(self, upgrades, security_upgrades, packages, reboot_required, upg_path,
    			 *args):
        QApplication.__init__(self, *args)
        self.dialog = Dialog(upgrades, security_upgrades, packages, reboot_required,
        					 upg_path)
        self.dialog.show()

def main(args, upgrades, security_upgrades, packages, reboot_required, upg_path):
    global app
    app = App(upgrades, security_upgrades, packages, reboot_required, upg_path, args)
    app.setWindowIcon(QIcon.fromTheme("system-software-update"))
    app.exec_()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p",
                      "--upgrader-sw",
                      dest="upg_path",
                      help="Define software/app to open for upgrade",
                      metavar="APP")


    (options, args) = parser.parse_args()

    worker = update_worker_t()
    #worker.check_for_updates()
    worker.check_updates_names()
    print(worker.packages)
    print(worker.upgrades)

    reboot_required_path = Path("/var/run/reboot-required")
    if reboot_required_path.exists():
        reboot_required = True
    else:
        reboot_required = False

    if worker.upgrades > 0 or reboot_required:
        main(sys.argv, worker.upgrades, worker.security_upgrades, worker.packages,
        		reboot_required, options.upg_path)

    sys.exit(0)
