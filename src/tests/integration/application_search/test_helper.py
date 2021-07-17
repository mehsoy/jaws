#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import subprocess


class TestHelper:
    @staticmethod
    def destroy_test_evironment(test_dir: str):
        #now we can just remove all
        TestHelper.remove_dir(test_dir + "/*")
        #TestHelper._mkdir(test_dir)

    @staticmethod
    def build_test_environment(test_dir: str):
        #just to avoid conflicts in mkdir
        TestHelper.destroy_test_evironment(test_dir)
        #build directories
        TestHelper._mkdir(test_dir + "user1ldap-first_directory")
        TestHelper._mkdir(test_dir + "user1ldap-first_directory/subdir")
        TestHelper._mkdir(test_dir + "user1ldap-second_directory")
        TestHelper._mkdir(test_dir + "user1ldap-second_directory/subdir")
        
        TestHelper._mkdir(test_dir + "user2ldap-first_directory")
        TestHelper._mkdir(test_dir + "user2ldap-first_directory/subdir")
        TestHelper._mkdir(test_dir + "user2ldap-second_directory")
        TestHelper._mkdir(test_dir + "user2ldap-second_directory/subdir")
        
        #TestHelper._mkfile(test_dir + "testfile-1.txt", "test successful\nother value")
   
    @staticmethod
    def remove_file(path: str):
        cmd = ["rm", "-f", path]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
    
    @staticmethod
    def remove_dir(path: str):
        cmd = ["rm", "-rf", path]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)

    @staticmethod
    def _mkdir(path: str):
        cmd = ["mkdir", path]
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)

    @staticmethod
    def _mkfile(path: str, content: str):
        subprocess.check_output('echo "' + content + '" > ' + path, universal_newlines=True , shell = True)
