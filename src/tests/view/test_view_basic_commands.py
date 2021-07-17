#!/usr/bin/python
# -*- coding: utf-8 -*-
import pytest

import sys
import requests

from views.CmdView.command_line import CommandLine

#
#These Test tests the parser and command creation
#


# TEST FOR THE ACTIVE COMMAND

@pytest.mark.order2
def test_activate_worker():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'activate' , 'worker' , '--id','20']
        CommandLine().process()

@pytest.mark.order3
def test_activate_master():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'activate' , 'master' ]
        CommandLine().process()

@pytest.mark.order4
def test_activate_storage():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'activate' , 'storage' , '--id','20']
        CommandLine().process()

@pytest.mark.order5
def test_activate_nonvalid(capfd):

        sys.argv = ['dmd', 'activate' , 'A' , '--id','20']
        CommandLine().process()
        out,err = capfd.readouterr()
        assert out == 'Object A not known\n'

# TEST FOR THE DEACTIVE COMMAND

@pytest.mark.order6
def test_activate_nonvalid2(capfd):
    with pytest.raises(SystemExit):
        sys.argv = ['dmd', 'activate' , 'storage'  ]
        CommandLine().process()
        out,err = capfd.readouterr()
        assert out == 'Id for Storage or Worker needed'

@pytest.mark.order7
def test_deactivate_worker():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'deactivate' , 'worker' , '--id','20']
        CommandLine().process()

@pytest.mark.order8
def test_deactivate_master():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'deactivate' , 'master' ]
        CommandLine().process()

@pytest.mark.order9
def test_deactivate_storage():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'deactivate' , 'storage' , '--id','20']
        CommandLine().process()

@pytest.mark.order10
def test_deactivate_nonvalid(capfd):

        sys.argv = ['dmd', 'deactivate' , 'A' , '--id','20']
        CommandLine().process()
        out,err = capfd.readouterr()
        assert out == 'Object A not known\n'

@pytest.mark.order11
def test_deactivate_nonvalid2(capfd):
    with pytest.raises(SystemExit):
        sys.argv = ['dmd', 'deactivate' , 'storage'  ]
        CommandLine().process()
        out,err = capfd.readouterr()
        assert out == 'Id for Storage or Worker needed'

# Test for the cancel command

@pytest.mark.order12
def test_cancel():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'cancel','20']
        CommandLine().process()

@pytest.mark.order13
def test_cancel_notvalid(capfd):
    with pytest.raises(SystemExit):
        sys.argv = ['dmd', 'cancel','sadsaa']
        CommandLine().process()


# Test for the active command

@pytest.mark.order14
def test_active_valid_allParams(capfd):
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'active' ,'-user', 'baum','-all'  ]
        CommandLine().process()

@pytest.mark.order15
def test_active_valid_noParams(capfd):
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'active']
        CommandLine().process()

# TEST FOR THE MOVE COMMAND

@pytest.mark.order16
def test_move():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'move' , 'source' , 'target']
        CommandLine().process()


@pytest.mark.order17
def test_move_params():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'move', 'source', 'target','-a','-b','-e','-user','baum']
        CommandLine().process()

@pytest.mark.order18
def test_move_nonvalid_params():
    with pytest.raises(SystemExit):
        sys.argv = ['dmd', 'move', 'source','basdasd', 'target','-a','-b','-e','-user','baum']
        CommandLine().process()

# TEST FOR THE WORKERS COMMAND

@pytest.mark.order19
def test_workes():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'workers']
        CommandLine().process()

@pytest.mark.order20
def test_workes_nonvalid():
    with pytest.raises(SystemExit):
        sys.argv = ['dmd', 'workers','param']
        CommandLine().process()

@pytest.mark.order21
def test_workes():
    with pytest.raises(requests.exceptions.ConnectionError):
        sys.argv = ['dmd', 'workers']
        CommandLine().process()






















