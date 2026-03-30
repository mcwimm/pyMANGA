#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ProjectLib.helpers import getInputParameters


class DisturbanceModel:
    """
    Base class for all disturbance concepts (e.g. Hurricane, Lightning).
    Provides shared parameter parsing and interface methods.
    """

    def getInputParameters(self, **tags):
        """
        Read module tags from project file.
        Args:
            tags (dict): dictionary containing tags from project file,
                         required and optional tag names.
        """
        getInputParameters(self, **tags)

    def getConceptName(self):
        """
        Return name of disturbance concept.
        Returns:
            string
        """
        return type(self).__name__

    def apply(self, t_ini, t_end, plants):
        """
        Apply disturbance for a single timestep.
        Args:
            t_ini (float): start time of the timestep (seconds)
            t_end (float): end time of the timestep (seconds)
            plants (list): collection of plant objects
        """
        raise NotImplementedError
