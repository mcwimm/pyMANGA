# Description

This module simulates small-scale lightning strike disturbances as described in scenario 2 of Vogt et al. (2014, Ecological Complexity 20:107-115).

Every simulation year, `n_patches` circular gaps are created at random positions within the simulation domain.
Gap radii are drawn from a uniform distribution U(`radius_min`, `radius_max`).
All trees inside the gaps are killed with probability `mortality_frac` (default 1.0, i.e. complete removal).

All default values are based on Vogt et al. (2014).

# Usage

```xml
<disturbance>
    <Lightning>
        <n_patches> 3 </n_patches>
        <radius_min> 6.0 </radius_min>
        <radius_max> 12.0 </radius_max>
        <mortality_frac> 1.0 </mortality_frac>
        <x_1> 0 </x_1>
        <x_2> 22 </x_2>
        <y_1> 0 </y_1>
        <y_2> 22 </y_2>
    </Lightning>
</disturbance>
```

# Attributes

- ``n_patches`` (int): number of gaps created per year (default: 3)
- ``radius_min`` (float): minimum gap radius in meters (default: 6.0)
- ``radius_max`` (float): maximum gap radius in meters (default: 12.0)
- ``mortality_frac`` (float): probability of mortality for trees inside a gap (default: 1.0)
- ``x_1``, ``x_2``, ``y_1``, ``y_2`` (float): domain bounds for gap placement (optional; derived from plant positions if omitted)
- ``verbose`` (bool): enable debug output (default: False)

# Details

## Process overview

Each simulation year, the module:

1. Places `n_patches` gap centers at random positions within the domain.
2. Draws each gap radius from U(`radius_min`, `radius_max`).
3. Kills all trees inside any gap with probability `mortality_frac`.

The death probability per tree per year is (Eq. 6 in Vogt et al. 2014):

$$P_{ls} = \frac{A_{ls}}{A} = \frac{n_{patches} \times r_{ls}^2 \times \pi}{A}$$

where $A_{ls}$ is the total gap area and $A$ is the simulation area.

# References

<a href="https://doi.org/10.1016/j.ecocom.2014.09.008" target="_blank">Vogt et al., 2014</a>

# Author(s)

Guanzhen Liu

# See Also

`pyMANGA.DisturbanceLib`, `pyMANGA.DisturbanceLib.Hurricane`
