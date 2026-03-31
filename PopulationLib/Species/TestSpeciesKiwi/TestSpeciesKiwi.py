#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test species for multi-species FON benchmark.
Based on AvicenniaKiwi but with different FON parameters (aa, bb, fmin)
to verify per-plant parameter handling in FON module.
"""


def createPlant():
    geometry = {}
    parameter = {}
    geometry["r_stem"] = 0.005                          # m
    parameter["salt_effect_d"] = -0.18
    parameter["salt_effect_ui"] = 72
    parameter["max_height"] = 3500                      # cm
    parameter["max_dbh"] = 140                          # cm
    parameter["max_growth"] = 162                       # cm
    parameter["b2"] = 48.04
    parameter["b3"] = 0.172
    parameter["mortality_constant"] = 0.467
    parameter["a_zoi_scaling"] = 10
    geometry["r_bg"] = parameter["a_zoi_scaling"] * geometry["r_stem"]**0.5
    geometry["r_ag"] = geometry["r_bg"]
    dbh_cm = geometry["r_stem"] * 200                   # cm
    height_cm = (137 + parameter["b2"] * dbh_cm - parameter["b3"] * dbh_cm ** 2)
    geometry["height"] = height_cm / 100                # m
    # resource module FixedSalinity
    parameter["r_salinity"] = "forman"
    # resource module FON — different from AvicenniaKiwi (aa=10, bb=1, fmin=0.1)
    parameter["aa"] = 15
    parameter["bb"] = 0.5
    parameter["fmin"] = 0.15
    return geometry, parameter
