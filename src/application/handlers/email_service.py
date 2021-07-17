#!/usr/bin/python
#-*- coding: utf-8 -*-
from application.system.user import User
import os


class EmailService:

    SENDMAIL = "/usr/sbin/sendmail"
    SUBJECT = "Task notification"
    SENDER = "DMD"

    def __init__(self, email_domain):
        self.email_domain = email_domain

    def mail(self, users, message, addresses=None):
        if users is not None:
            for user in users:
                address = self.get_user_email(user)
                self.send(address, message)
        if addresses is not None:
            for address in addresses:
                self.send(address, message)

    def send(self, address, message):

        p = os.popen(self.SENDMAIL + " -t", "w")
        p.write("To: " + address + "\n")
        p.write("Subject: " + self.SUBJECT + "\n")
        p.write("From: " + self.SENDER + "\n")
        p.write("\n")       # blank line separating headers from body
        p.write(message + "\n")
        status = p.close()
        if status == 0:
            print("Error 0")

    def get_user_email(self, user):
        """
        Simple solution for email lookups
        :param user: User
        :return: email address
        """
        return user.get_username() + "@" + self.email_domain
