#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import sys
from os import path
from ProjectLib import XMLtoProject
from TimeLoopLib import TreeDynamicTimeStepping
import logging


class Model():
    ## Class to run the model from other programs
    #  @param project_file: path to pymanga project file.
    #  @date: 2021 - Today
    #  @author: jasper.bathmann@ufz.de
    def __init__(self, project_file):
        self.prj = XMLtoProject(xml_project_file=project_file)
        self.t_step_begin = 0

    def createExternalTimeStepper(self, t_0=0):
        from TimeLoopLib import ExternalDynamicTimeStepping
        self.timestepper = ExternalDynamicTimeStepping(self.prj, t_0)

    ## This call propagates the model from the last timestep.
    #  Default starting point is t=0 and will be updated with every call
    #  @param t: time, for end of next timestep
    def propagateModel(self, t):
        self.timestepper.step(t)
        self.t_step_begin = t

    def setBelowgroundInformation(self, **args):
        self.prj.getBelowgroundCompetition().setExternalInformation(**args)

    ## Getter for external information
    def getBelowgroundInformation(self):
        return self.prj.getBelowgroundCompetition().getExternalInformation()


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:l:", ["project_file=", "logging"])
    except getopt.GetoptError:
        print("""pyMANGA wrong usage. Type "python main.py -h"
  for additional help.""")
        sys.exit(0)
    for opt, arg in opts:
        if opt == '-h':
            print("""pyMANGA arguments:
  -i,--project_file <path/to/xml/project/file>""")
            sys.exit()
        elif opt in ("-i", "--project_file"):
            project_file = str(arg)
        elif opt in ("-l", "--project_file"):
            project_file = str(arg)
            logging.basicConfig(filename='MANGA.log',
                                level=logging.INFO,
                                filemode='w',   # overwrite existing log file
                                format='%(asctime)s %(message)s')
            print('Logging mode\n')
    try:
        prj = XMLtoProject(xml_project_file=project_file)
    except UnboundLocalError:
        raise UnboundLocalError('Wrong usage of pyMANGA. Type "python' +
                                ' main.py -h" for additional help.')
    print('Running pyMANGA project ', project_file)
    time_stepper = TreeDynamicTimeStepping(prj)
    prj.runProject(time_stepper)
    print('pyMANGA project ', project_file, ' successfully evaluated.')


if __name__ == "__main__":
    sys.path.append((path.dirname(path.abspath(__file__))))
    main(sys.argv[1:])
