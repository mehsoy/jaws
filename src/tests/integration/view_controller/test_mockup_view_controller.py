#!/usr/bin/python
# -*- coding: utf-8 -*-




import subprocess
import sys
from views.CmdView.command_line import CommandLine
import pytest



@pytest.fixture()
def app():

    return subprocess.Popen(['python3','src/tests/integration/view_controller/rest_api_mockuptest.py','&'],universal_newlines=True,shell=True)


def test_target_list(app,capfd):

        cookies = {
            'user': 'centos',
            'token': 'PZ151XH7A1'
            }

        body =  {
            'source': 'blablubb/blubb',
            'target': 'blablubb'
        }


        sys.argv = ['dmd', 'move', 'blablubb/blubb', 'blablubb']

        CommandLine().process()
        out,err = capfd.readouterr()

        assert out is '''{ 'job_id': 5 }'''

        subprocess.Popen.kill(app)







