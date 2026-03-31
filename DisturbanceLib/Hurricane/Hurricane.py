#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hurricane disturbance module (large-scale, patch-forming events).

Timestep-based implementation of scenario 3 in
Vogt et al. (2014, Ecological Complexity 20:107-115).

Each year, a hurricane occurs with probability `frequency` (default 0.05,
i.e. once every 20 years on average). Each event creates `n_patches`
circular patches at random positions within the domain. Inside patches,
trees are killed with DBH-dependent probabilities.
"""
import math
import numpy as np
from DisturbanceLib.DisturbanceModel import DisturbanceModel

SECONDS_PER_YEAR = 3600.0 * 24.0 * 365.25


class Hurricane(DisturbanceModel):
    """
    Hurricane disturbance concept.
    """

    def __init__(self, args, project=None):
        """
        Args:
            args (lxml.etree._Element): <Hurricane> section from project file
            project: MangaProject object (optional)
        """
        tags = {
            "prj_file": args,
            "optional": ["frequency", "n_patches", "patch_radius",
                         "dbh_threshold", "mort_tall", "mort_small",
                         "x_1", "x_2", "y_1", "y_2", "verbose"]
        }
        super().getInputParameters(**tags)

        # Set defaults for missing optional parameters
        if not hasattr(self, "frequency"):
            self.frequency = 0.05
        if not hasattr(self, "n_patches"):
            self.n_patches = 3
        else:
            self.n_patches = int(self.n_patches)
        if not hasattr(self, "patch_radius"):
            self.patch_radius = 51.0
        self.patch_radius = max(0.0, self.patch_radius)
        if not hasattr(self, "dbh_threshold"):
            self.dbh_threshold = 0.15
        if not hasattr(self, "mort_tall"):
            self.mort_tall = 0.75
        self.mort_tall = max(0.0, min(1.0, self.mort_tall))
        if not hasattr(self, "mort_small"):
            self.mort_small = 0.50
        self.mort_small = max(0.0, min(1.0, self.mort_small))
        if not hasattr(self, "verbose"):
            self.verbose = False
        else:
            self.verbose = str(self.verbose).strip().lower() in ("true", "1", "yes", "y")

        # Domain bounds (optional)
        if not hasattr(self, "x_1"):
            self.x_1 = None
        if not hasattr(self, "x_2"):
            self.x_2 = None
        if not hasattr(self, "y_1"):
            self.y_1 = None
        if not hasattr(self, "y_2"):
            self.y_2 = None

        self._last_year = -1

        if self.verbose:
            print("[HURRICANE][INIT] frequency={}, n_patches={}, "
                  "radius={:.2f}, dbh_threshold={:.2f}, "
                  "mort_tall={:.2f}, mort_small={:.2f}".format(
                      self.frequency, self.n_patches, self.patch_radius,
                      self.dbh_threshold, self.mort_tall, self.mort_small))

    def apply(self, t_ini, t_end, plants):
        """
        Apply hurricane disturbance for a single timestep.
        Args:
            t_ini (float): start time of the timestep (seconds)
            t_end (float): end time of the timestep (seconds)
            plants (list): collection of plant objects
        """
        if not plants or self.frequency <= 0.0:
            return

        current_year = int(t_ini / SECONDS_PER_YEAR)
        if current_year == self._last_year:
            return
        self._last_year = current_year

        if np.random.random() >= self.frequency:
            return

        self._applyPatchMortality(plants, current_year)

    def _applyPatchMortality(self, plants, current_year=None):
        """
        Apply DBH-dependent mortality inside circular patches.
        Args:
            plants (list): collection of plant objects
            current_year (int): current simulation year (for verbose output)
        """
        x_1, x_2, y_1, y_2 = self._getDomain(plants)
        if x_1 >= x_2 or y_1 >= y_2:
            print("WARNING: Hurricane disturbance skipped due to invalid domain bounds.")
            return

        if self.n_patches <= 0 or self.patch_radius <= 0.0:
            return

        cx = np.random.uniform(x_1, x_2, size=self.n_patches)
        cy = np.random.uniform(y_1, y_2, size=self.n_patches)
        r2 = self.patch_radius * self.patch_radius

        alive = []
        for plant in plants:
            if not plant.getSurvival():
                continue
            x, y = float(plant.x), float(plant.y)
            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            alive.append((x, y, self._getDBH(plant), plant))

        if not alive:
            return

        killed = 0
        for x, y, dbh, plant in alive:
            in_patch = False
            for k in range(self.n_patches):
                dx, dy = x - cx[k], y - cy[k]
                if dx * dx + dy * dy <= r2:
                    in_patch = True
                    break
            if not in_patch:
                continue

            p_kill = self.mort_tall if (math.isfinite(dbh) and dbh >= self.dbh_threshold) else self.mort_small
            if p_kill > 0.0 and np.random.random() < p_kill:
                plant.setSurvival(0)
                plant.getGrowthConceptInformation()["mortality_cause"] = "Hurricane"
                killed += 1

        if self.verbose:
            print("[HURRICANE] year={}, patches={}, plants={}, killed={}".format(
                current_year, self.n_patches, len(alive), killed))

    def _getDBH(self, plant):
        """
        Compute DBH (m) from plant geometry: DBH = 2 * r_stem.
        Args:
            plant: plant object
        Returns:
            float
        """
        if not hasattr(plant, "getGeometry"):
            return float("nan")
        geo = plant.getGeometry()
        if "r_stem" not in geo:
            return float("nan")
        return 2.0 * float(geo["r_stem"])

    def _getDomain(self, plants):
        """
        Return domain bounds (x_1, x_2, y_1, y_2).
        Uses XML values if provided, otherwise derives from plant positions.
        """
        if (self.x_1 is not None and self.x_2 is not None and
                self.y_1 is not None and self.y_2 is not None):
            return self.x_1, self.x_2, self.y_1, self.y_2
        xs = [float(p.x) for p in plants if hasattr(p, "x")]
        ys = [float(p.y) for p in plants if hasattr(p, "y")]
        if not xs or not ys:
            return 0, 0, 0, 0
        return min(xs), max(xs), min(ys), max(ys)
