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

SECONDS_PER_YEAR = 3600.0 * 24.0 * 365.25


class Hurricane:
    """
    Hurricane disturbance concept.
    """

    def __init__(self, args, project=None):
        """
        Args:
            args (lxml.etree._Element): <Hurricane> section from project file
            project: MangaProject object (optional)
        """
        self.verbose = (
            args.findtext("verbose", "False").strip().lower()
            in ("true", "1", "yes", "y"))

        # Annual probability of a hurricane event (Vogt 2014: f_h = 0.05)
        self.frequency = float(args.findtext("frequency", "0.05"))

        # Patch configuration
        self.n_patches = int(args.findtext("n_patches", "3"))
        self.patch_radius = max(0.0, float(args.findtext("patch_radius", "51.0")))

        # DBH-dependent mortality (Vogt 2014: dbh_h = 15 cm)
        self.dbh_threshold = float(args.findtext("dbh_threshold", "15.0"))
        self.mort_tall = max(0.0, min(1.0, float(args.findtext("mort_tall", "0.75"))))
        self.mort_small = max(0.0, min(1.0, float(args.findtext("mort_small", "0.50"))))

        # Domain bounds for random patch placement
        self._x_1 = self._readFloat(args, "x_1", None)
        self._x_2 = self._readFloat(args, "x_2", None)
        self._y_1 = self._readFloat(args, "y_1", None)
        self._y_2 = self._readFloat(args, "y_2", None)

        self._last_year = -1

        if self.verbose:
            print("[HURRICANE][INIT] frequency={}, n_patches={}, "
                  "radius={:.2f}, dbh_threshold={:.2f}, "
                  "mort_tall={:.2f}, mort_small={:.2f}".format(
                      self.frequency, self.n_patches, self.patch_radius,
                      self.dbh_threshold, self.mort_tall, self.mort_small))

    def getConceptName(self):
        """Return name of disturbance concept."""
        return type(self).__name__

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

        # Stochastic trigger: Bernoulli trial with annual probability
        if np.random.random() >= self.frequency:
            return

        if self.verbose:
            print("[HURRICANE] year={}, event=YES, plants={}".format(
                current_year, len(plants)))

        self._applyPatchMortality(plants)

    def _applyPatchMortality(self, plants):
        """
        Apply DBH-dependent mortality inside circular patches.
        Patch centers are placed at random positions in the domain.
        Args:
            plants (list): collection of plant objects
        """
        # Determine domain bounds
        x_1, x_2, y_1, y_2 = self._getDomain(plants)
        if x_1 >= x_2 or y_1 >= y_2:
            return

        if self.n_patches <= 0 or self.patch_radius <= 0.0:
            return

        # Random patch centers within domain (Vogt 2014: uniform randomly distributed)
        cx = np.random.uniform(x_1, x_2, size=self.n_patches)
        cy = np.random.uniform(y_1, y_2, size=self.n_patches)
        r2 = self.patch_radius * self.patch_radius

        # Collect alive plants and their DBH
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

        # Find plants inside any patch, apply DBH-dependent mortality
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
                killed += 1

        if self.verbose:
            print("[HURRICANE] patches={}, alive={}, killed={}".format(
                self.n_patches, len(alive), killed))

    def _getDBH(self, plant):
        """
        Compute DBH (cm) from plant geometry: DBH = 2 * r_stem(m) * 100.
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
        return 2.0 * float(geo["r_stem"]) * 100.0

    def _getDomain(self, plants):
        """
        Return domain bounds (x_1, x_2, y_1, y_2).
        Uses XML values if provided, otherwise derives from plant positions.
        """
        if (self._x_1 is not None and self._x_2 is not None and
                self._y_1 is not None and self._y_2 is not None):
            return self._x_1, self._x_2, self._y_1, self._y_2
        xs = [float(p.x) for p in plants if hasattr(p, "x")]
        ys = [float(p.y) for p in plants if hasattr(p, "y")]
        if not xs or not ys:
            return 0, 0, 0, 0
        return min(xs), max(xs), min(ys), max(ys)

    def _readFloat(self, args, tag, default):
        text = args.findtext(tag, None)
        if text is None:
            return default
        return float(text.strip())
