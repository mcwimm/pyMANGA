# Description

This module simulates large-scale hurricane disturbances as described in scenario 3 of Vogt et al. (2014, Ecological Complexity 20:107-115).

Each simulation year, a hurricane event occurs with a given probability (`frequency`, default 0.05, i.e. once every 20 years on average).
When an event occurs, `n_patches` circular patches are placed at random positions within the simulation domain.
Inside these patches, trees are killed with DBH-dependent probabilities.

All default values are based on Vogt et al. (2014).

# Usage

```xml
<disturbance>
    <Hurricane>
        <frequency> 0.05 </frequency>
        <n_patches> 3 </n_patches>
        <patch_radius> 51.0 </patch_radius>
        <dbh_threshold> 0.15 </dbh_threshold>
        <mort_tall> 0.75 </mort_tall>
        <mort_small> 0.50 </mort_small>
        <x_1> 0 </x_1>
        <x_2> 22 </x_2>
        <y_1> 0 </y_1>
        <y_2> 22 </y_2>
    </Hurricane>
</disturbance>
```

# Attributes

- ``frequency`` (float): annual probability of a hurricane event (default: 0.05)
- ``n_patches`` (int): number of circular patches per event (default: 3)
- ``patch_radius`` (float): radius of each patch in meters (default: 51.0)
- ``dbh_threshold`` (float): DBH threshold in meters (default: 0.15)
- ``mort_tall`` (float): mortality probability for trees with DBH >= threshold (default: 0.75)
- ``mort_small`` (float): mortality probability for trees with DBH < threshold (default: 0.50)
- ``x_1``, ``x_2``, ``y_1``, ``y_2`` (float): domain bounds for patch placement (optional; derived from plant positions if omitted)
- ``verbose`` (bool): enable debug output (default: False)

# Details

## Process overview

Each simulation year, the module:

1. Performs a Bernoulli trial with probability `frequency` to determine if a hurricane occurs.
2. If triggered, places `n_patches` circular patches at random positions within the domain.
3. For each alive plant inside any patch, computes DBH from `r_stem`: DBH (m) = 2 * r_stem.
4. Applies mortality with probability `mort_tall` (DBH >= `dbh_threshold`) or `mort_small` (DBH < `dbh_threshold`).

The death probability per tree per year is (Eq. 7 in Vogt et al. 2014):

$$P_h = f_h \times \frac{A_h}{A} \times (p \times mort_{tall} + (1-p) \times mort_{small})$$

where $A_h = n_{patches} \times r_h^2 \times \pi$ is the total disturbed area and $p$ is the probability that DBH >= dbh_threshold.

# References

<a href="https://doi.org/10.1016/j.ecocom.2014.09.008" target="_blank">Vogt et al., 2014</a>

# Author(s)

Guanzhen Liu

# See Also

`pyMANGA.DisturbanceLib`, `pyMANGA.DisturbanceLib.Lightning`
