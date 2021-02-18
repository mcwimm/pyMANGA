#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@date: 2021-Today
@author: marie-christin.wimmler@tu-dresden.de
"""

##########################
# MACHT NOCH KEINEN SINN #
##########################

import numpy as np
from TreeModelLib.BelowgroundCompetition import BelowgroundCompetition
from TreeModelLib.BelowgroundCompetition.Network import Network


class NetworkFON(Network):
    ## FON case for belowground competition concept. For details see
    #  (https://doi.org/10.1016/S0304-3800(00)00298-2). FON returns a list
    #  of multipliers for each tree for salinity and competition.\n
    #  @param: Tags to define FON, see tag documentation \n
    #  @date: 2019 - Today
    def __init__(self, args):
        case = args.find("type").text
        print("Initiate belowground competition of type " + case + ".")
        self.makeGrid(args)

    def calculateBelowgroundResources(self):
        # FON start
        distance = (((self._my_grid[0][:, :, np.newaxis] -
                      np.array(self._xe)[np.newaxis, np.newaxis, :])**2 +
                     (self._my_grid[1][:, :, np.newaxis] -
                      np.array(self._ye)[np.newaxis, np.newaxis, :])**2)**0.5)
        my_fon = self.calculateFonFromDistance(np.array(self._r_stem),
                                               distance)
        fon_areas = np.zeros_like(my_fon)
        #Add a one, where tree is larger than 0
        fon_areas[np.where(my_fon > 0)] += 1
        #Count all nodes, which are occupied by trees
        #returns array of shape (ntrees)
        fon_areas = fon_areas.sum(axis=(0, 1))
        fon_heigths = my_fon.sum(axis=-1)
        fon_impacts = fon_heigths[:, :, np.newaxis] - my_fon
        fon_impacts[np.where(my_fon < self._fmin)] = 0
        fon_impacts = fon_impacts.sum(axis=(0, 1))
        resource_limitations = 1 - 2 * fon_impacts / fon_areas
        resource_limitations[np.where(resource_limitations < 0)] = 0
        salinity_reductions = (1 / (1 + np.exp(
            np.array(self._salt_effect_d) *
            (np.array(self._salt_effect_ui) - self._salinity))))
        FON_factor = resource_limitations * salinity_reductions
        # FON end

        self.groupFormation()
        self.rootGraftFormation()
        self.calculateBGresourcesTree()
        res_b = self.getBGresourcesIndividual(self._psi_top, self._psi_osmo,
                                              self._above_graft_resistance,
                                              self._below_graft_resistance)
        self.belowground_resources = self._water_avail / res_b * FON_factor

        for i, tree in zip(range(0, self.n_trees), self.trees):
            network = {}
            network['partner'] = self._partner_names[i]
            network['rgf'] = self._rgf_counter[i]
            network['potential_partner'] = self._potential_partner[i]
            network['water_available'] = self._water_avail[i] * FON_factor
            network['water_absorbed'] = self._water_absorb[i] * FON_factor
            network['water_exchanged'] = self._water_exchanged_trees[i] * FON_factor

            tree.setNetwork(network)

    ## This function returns the fon height of a tree on the mesh.\n
    #  @param rst - FON radius\n
    #  @param distance - array of distances of all mesh points to tree position
    def calculateFonFromDistance(self, rst, distance):
        fon_radius = self._aa * rst**self._bb
        cc = -np.log(self._fmin) / (fon_radius - rst)
        height = np.exp(-cc[np.newaxis, np.newaxis, :] *
                        (distance - rst[np.newaxis, np.newaxis, :]))
        height[height > 1] = 1
        height[height < self._fmin] = 0
        return height

    ## This function initialises the mesh.\n
    def makeGrid(self, args):
        missing_tags = [
            "type", "domain", "x_1", "x_2", "y_1", "y_2", "x_resolution",
            "y_resolution", "aa", "bb", "fmin", "salinity"
        ]
        for arg in args.iterdescendants():
            tag = arg.tag
            if tag == "x_resolution":
                x_resolution = int(arg.text)
            if tag == "y_resolution":
                y_resolution = int(arg.text)
            elif tag == "x_1":
                x_1 = float(arg.text)
            elif tag == "x_2":
                x_2 = float(arg.text)
            elif tag == "y_1":
                y_1 = float(arg.text)
            elif tag == "y_2":
                y_2 = float(arg.text)
            elif tag == "aa":
                self._aa = float(arg.text)
            elif tag == "bb":
                self._bb = float(arg.text)
            elif tag == "fmin":
                self._fmin = float(arg.text)
            elif tag == "salinity":
                self._salinity = float(arg.text)
            try:
                missing_tags.remove(tag)
            except ValueError:
                raise ValueError(
                    "Tag " + tag +
                    " not specified for below-ground grid initialisation!")
        if len(missing_tags) > 0:
            string = ""
            for tag in missing_tags:
                string += tag + " "
            raise KeyError(
                "Tag(s) " + string +
                "are not given for below-ground grid initialisation in project file."
            )
        l_x = x_2 - x_1
        l_y = y_2 - y_1
        x_step = l_x / x_resolution
        y_step = l_y / y_resolution
        self._mesh_size = np.maximum(x_step, y_step)
        xe = np.linspace(x_1 + x_step / 2.,
                         x_2 - x_step / 2.,
                         x_resolution,
                         endpoint=True)
        ye = np.linspace(y_1 + y_step / 2.,
                         y_2 - y_step / 2.,
                         y_resolution,
                         endpoint=True)
        self._my_grid = np.meshgrid(xe, ye)

    ## This functions prepares the competition concept for the competition
    #  concept. In the FON concept, tree's allometric measures are saved
    #  in simple lists and the timestepping is updated. A mesh-like array
    #  is prepared for storing all FON heights of the stand.\n
    #  @param t_ini - initial time for next timestep \n
    #  @param t_end - end time for next timestep
    def prepareNextTimeStep(self, t_ini, t_end):
        # FON start
        self._fon_area = []
        self._fon_impact = []
        self._resource_limitation = []
        self._salinity_reduction = []
        self._xe = []
        self._ye = []
        self._salt_effect_d = []
        self._salt_effect_ui = []
        self._r_stem = []
        self._t_ini = t_ini
        self._t_end = t_end
        self._fon_height = np.zeros_like(self._my_grid[0])
        # FON end

        self.trees = []

        self._tree_name = np.empty(0)
        self._partner_names = []
        self._partner_indices = []
        self._potential_partner = []
        self._rgf_counter = []

        self.graph_dict = {}
        self._gIDs = []

        self._above_graft_resistance = np.empty(0)
        self._below_graft_resistance = np.empty(0)
        self._psi_height = []
        self._psi_leaf = []
        self._psi_osmo = []
        self._psi_top = []
        self._r_root = []
        self._kf_sap = []

        self.belowground_resources = []

        self.time = t_end - t_ini

    ## Before being able to calculate the resources, all tree entities need
    #  to be added with their relevant allometric measures for the next timestep.
    #  @param: tree
    def addTree(self, tree):
        # FON start
        if self._mesh_size > 0.25:
            print("Error: mesh not fine enough for FON!")
            print("Please refine mesh to grid size < 0.25m !")
            exit()
        x, y = tree.getPosition()
        geometry = tree.getGeometry()
        parameter = tree.getParameter()
        self._xe.append(x)
        self._ye.append(y)
        self._salt_effect_d.append(parameter["salt_effect_d"])
        self._salt_effect_ui.append(parameter["salt_effect_ui"])
        self._r_stem.append(geometry["r_stem"])
        # FON end
        # network start
        self.network = tree.getNetwork()
        self.trees.append(tree)
        self._rgf_counter.append(self.network['rgf'])
        self._partner_names.append(self.network['partner'])
        self._potential_partner.append(self.network['potential_partner'])
        self.n_trees = len(self._xe)
        self._tree_name = np.concatenate((self._tree_name,
                                          [str(tree.group_name) + str(tree.tree_id)]))
        self._below_graft_resistance = np.concatenate((self._below_graft_resistance,
                                                       [self.belowGraftResistance(parameter["lp"],
                                                                                  parameter["k_geom"],
                                                                                  parameter["kf_sap"],
                                                                                  geometry["r_root"],
                                                                                  geometry["h_root"],
                                                                                  geometry["r_stem"])]
                                                       ))
        self._above_graft_resistance = np.concatenate((self._above_graft_resistance,
                                                       [self.aboveGraftResistance(
                                                           parameter["kf_sap"], geometry["r_crown"],
                                                           geometry["h_stem"], geometry["r_stem"])]
                                                       ))

        self._r_root.append(geometry["r_root"])
        self._psi_leaf.append(parameter["leaf_water_potential"])
        self._psi_height.append((2 * geometry["r_crown"] + geometry["h_stem"]) * 9810)
        self._psi_top = np.array(self._psi_leaf) - np.array(self._psi_height)
        # ToDo: Woher kommt psi_osmo?
        sal = 0
        self._psi_osmo = np.array([sal] * self.n_trees)

        self._kf_sap.append(parameter["kf_sap"])