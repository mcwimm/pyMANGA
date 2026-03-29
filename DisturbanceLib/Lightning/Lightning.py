#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightning disturbance module (small-scale, gap-forming events).

Timestep-based implementation of scenario 2 in
Vogt et al. (2014, Ecological Complexity 20:107-115).

Every simulation year, `n_patches` circular gaps are created at random
positions within the domain. Gap radii are drawn from U(radius_min,
radius_max). All trees inside gaps are removed (mortality_frac = 1.0).
"""
import math
import numpy as np

SECONDS_PER_YEAR = 3600.0 * 24.0 * 365.25


class Lightning:
    """
    Lightning disturbance concept.
    """

    def __init__(self, args, project=None):
        """
        Args:
            args (lxml.etree._Element): <Lightning> section from project file
            project: MangaProject object (optional)
        """
        self.verbose = (
            args.findtext("verbose", "False").strip().lower()
            in ("true", "1", "yes", "y"))

        # Gap configuration (Vogt 2014: 3 gaps, r ~ U(6, 12) m)
        self.n_patches = int(args.findtext("n_patches", "3"))
        self.radius_min = max(0.0, float(args.findtext("radius_min", "6.0")))
        self.radius_max = float(args.findtext("radius_max", "12.0"))
        if self.radius_max < self.radius_min:
            self.radius_max = self.radius_min

        # Mortality inside gaps (Vogt 2014: 100%)
        self.mortality_frac = max(0.0, min(1.0, float(args.findtext("mortality_frac", "1.0"))))

        # Domain bounds for random gap placement
        self._x_1 = self._readFloat(args, "x_1", None)
        self._x_2 = self._readFloat(args, "x_2", None)
        self._y_1 = self._readFloat(args, "y_1", None)
        self._y_2 = self._readFloat(args, "y_2", None)

        self._last_year = -1

        if self.verbose:
            print("[LIGHTNING][INIT] n_patches={}, radius_min={:.2f}, "
                  "radius_max={:.2f}, mortality_frac={:.3f}".format(
                      self.n_patches, self.radius_min,
                      self.radius_max, self.mortality_frac))

    def getConceptName(self):
        """Return name of disturbance concept."""
        return type(self).__name__

    def apply(self, t_ini, t_end, plants):
        """
        Apply lightning disturbance for a single timestep.
        Triggers once per simulation year (deterministic).
        Args:
            t_ini (float): start time of the timestep (seconds)
            t_end (float): end time of the timestep (seconds)
            plants (list): collection of plant objects
        """
        if not plants:
            return

        current_year = int(t_ini / SECONDS_PER_YEAR)
        if current_year == self._last_year:
            return
        self._last_year = current_year

        if self.verbose:
            print("[LIGHTNING] year={}, event=YES, plants={}".format(
                current_year, len(plants)))

        self._applyPatchMortality(plants)

    def _applyPatchMortality(self, plants):
        """
        Apply mortality inside circular gaps at random domain positions.
        Args:
            plants (list): collection of plant objects
        """
        x_1, x_2, y_1, y_2 = self._getDomain(plants)
        if x_1 >= x_2 or y_1 >= y_2:
            return

        if self.n_patches <= 0:
            return

        # Random gap centers within domain
        cx = np.random.uniform(x_1, x_2, size=self.n_patches)
        cy = np.random.uniform(y_1, y_2, size=self.n_patches)

        # Random radii ~ U(radius_min, radius_max)
        if self.radius_min == self.radius_max:
            radii = np.full(self.n_patches, self.radius_max)
        else:
            radii = np.random.uniform(self.radius_min, self.radius_max, size=self.n_patches)

        # Find alive plants inside any gap
        alive = []
        for plant in plants:
            if not plant.getSurvival():
                continue
            x, y = float(plant.x), float(plant.y)
            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            alive.append((x, y, plant))

        if not alive:
            return

        candidates = set()
        for k in range(self.n_patches):
            r2 = radii[k] * radii[k]
            if r2 <= 0.0:
                continue
            for x, y, plant in alive:
                dx, dy = x - cx[k], y - cy[k]
                if dx * dx + dy * dy <= r2:
                    candidates.add(plant)

        if not candidates:
            return

        # Kill plants inside gaps
        killed = 0
        p = self.mortality_frac
        for plant in candidates:
            if p >= 1.0 or np.random.random() < p:
                plant.setSurvival(0)
                killed += 1

        if self.verbose:
            print("[LIGHTNING] patches={}, alive={}, candidates={}, killed={}".format(
                self.n_patches, len(alive), len(candidates), killed))

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
