#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@date: 2021-Today
@author: marie-christin.wimmler@tu-dresden.de
"""

from TreeModelLib.GrowthAndDeathDynamics import GrowthAndDeathDynamics
from TreeModelLib.GrowthAndDeathDynamics.SimpleBettina import SimpleBettina
import numpy as np


class NetworkBettinaVar(SimpleBettina):
    ## NetworkBettina for death and growth dynamics. This module is implements ...
    #  @param Tags to define SimpleBettina: type
    #  @date 2019 - Today
    def __init__(self, args):
        case = args.find("type").text
        print("Growth and death dynamics of type " + case + ".")
        self.getInputParameters(args)

    def progressTree(self, tree, aboveground_resources, belowground_resources):
        network = tree.getNetwork()
        ## counter to track or define the time required for root graft formation,
        # if -1 no root graft formation takes place at the moment
        self.rgf = network['rgf']
        self.partner = network['partner']
        self.potential_partner = network['potential_partner']
        self.psi_osmo = network["psi_osmo"]

        if self.variant == "V2":
            self.r_gr_min = network['r_gr_min']
            self.r_gr_rgf = network['r_gr_rgf']
            self.l_gr_rgf = network['l_gr_rgf']
            self.weight_gr = network['weight_gr']

        self.name = str(tree.group_name) + str(tree.tree_id)
        # Simple bettina tree progress
        SimpleBettina.progressTree(self, tree, aboveground_resources,
                                   belowground_resources)

        network['rgf'] = self.rgf
        network['potential_partner'] = self.potential_partner
        network['partner'] = self.partner

        if self.variant == "V2":
            network['r_gr_min'] = self.r_gr_min
            network['r_gr_rgf'] = self.r_gr_rgf
            network['l_gr_rgf'] = self.l_gr_rgf
            network['weight_gr'] = self.weight_gr # ToDo muss weight_gr
            # wirklich in network sein?

        tree.setNetwork(network)
        if self.survive == 1:
            tree.setSurvival(1)
        else:
            tree.setSurvival(0)

    def treeGrowthWeights(self):
        if self.variant == 'V2':
            self.treeGrowthWeightsV2()
        else:
            SimpleBettina.treeGrowthWeights(self)

    def growthResources(self):
        if self.variant == "V1":
            self.growthResourcesV1()
        else:
            SimpleBettina.growthResources(self)

    def rootGraftFormation(self):
        if self.variant == 'V1':
            self.rootGraftFormationV1()
        if self.variant == 'V2':
            self.rootGraftFormationV2()

    ## This functions calculates the growths weights for distributing
    # biomass increment to the geometric (allometric) tree measures as
    # defined in SimpleBettina. In addition, the function calls the root
    # graft formation function, if the tree is currently in the process of
    # root graft formation.
    def treeGrowthWeightsV2(self):
        # Simple bettina get growth weigths
        SimpleBettina.treeGrowthWeights(self)

        # If self.r_gr_min exists the tree is currently in the process of rgf
        if self.r_gr_min:
            self.rootGraftFormation()
        else:
            self.weight_gr = 0

    ## This function calculates the available resources and the biomass
    # increment. In addition, this function reduces the available resources
    # if trees are in the grafting process and calls the root graft
    # formation manager
    def growthResourcesV1(self):
        # Simple bettina get growth resources
        SimpleBettina.growthResources(self)
        self.rootGraftFormation()

    ## This function reduces growth during the process of root graft formation.
    # It is assumed that the process will take 2 years (this is subject to
    # change).
    def rootGraftFormationV1(self):
        if self.rgf != -1:
            self.grow = self.grow * self.f_growth
            self.rgf = self.rgf + 1
            if round(self.rgf * self.time / 3600 / 24 / 365, 3) >= 2:
                self.rgf = -1
                self.partner.append(self.potential_partner)
                self.potential_partner = []

    ## This function simulated root graft formation and thereby reduces girth
    # growth during this process.
    def rootGraftFormationV2(self):
        # check if rgf is finished
        if self.r_gr_rgf >= self.r_gr_min[0]:
            print('RGF is finished after ' + str(self.rgf) + ' time ' \
                                                     'steps. Years: ' + str(
                self.rgf * self.time / 3600 / 24 / \
                365))
            # Append partner
            self.partner.append(self.potential_partner)
            # Reset rgf parameters
            self.r_gr_rgf = 0.004
            self.rgf = -1
            # analyse rgf duration
            self.potential_partner = []
            self.r_gr_min = []
        else:
            # if rgf is not finished, the grafted roots must grow
            self.weight_gr = self.weight_girthgrowth * self.f_growth
            inc_r_gr = (self.weight_gr * self.grow /
                        (2 * np.pi * self.l_gr_rgf * self.r_gr_rgf))
            self.r_gr_rgf += inc_r_gr
            # reduce girth growth factor
            self.weight_girthgrowth = self.weight_girthgrowth * (1 -
                                                                 self.f_growth)
            self.rgf += 1

    def getInputParameters(self, args):
        missing_tags = ["type", "variant", "f_growth"]
        for arg in args.iterdescendants():
            tag = arg.tag
            if tag == "variant":
                self.variant = args.find("variant").text
            #if self.variant != "V0":
            if tag == "f_growth":
                self.f_growth = float(args.find("f_growth").text)
            try:
                missing_tags.remove(tag)
            except ValueError:
                raise ValueError(
                    "Tag " + tag +
                    " not specified for growth and death initialisation!")
        if len(missing_tags) > 0:
            string = ""
            for tag in missing_tags:
                string += tag + " "
            raise KeyError(
                "Tag(s) " + string +
                "are not given for growth and death initialisation in "
                "project file."
            )