# Description

This module simulates large-scale hurricane disturbances as described in scenario 3 of Vogt et al. (2014, Ecological Complexity 20:107-115).

Each simulation year, a hurricane event occurs with a given probability (`frequency`, default 0.05, i.e. once every 20 years on average).
When an event occurs, `n_patches` circular patches are placed at random positions within the simulation domain.
Inside these patches, trees are killed with DBH-dependent probabilities:

- Trees with DBH >= `dbh_threshold`: killed with probability `mort_tall` (default 0.75)
- Trees with DBH < `dbh_threshold`: killed with probability `mort_small` (default 0.50)

DBH (cm) is computed as 2 * r_stem (m) * 100.

# Usage

```xml
<disturbance>
    <Hurricane>
        <frequency> 0.05 </frequency>
        <n_patches> 3 </n_patches>
        <patch_radius> 51.0 </patch_radius>
        <dbh_threshold> 15.0 </dbh_threshold>
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

- ``frequency`` (float): annual probability of a hurricane event (default: 0.05). Source: Vogt et al. 2014, f_h = 0.05.
- ``n_patches`` (int): number of circular patches per event (default: 3). Source: Vogt et al. 2014, no_h = 3.
- ``patch_radius`` (float): radius of each patch in meters (default: 51.0). Source: Vogt et al. 2014, Eq. 10, r_h = 51 m.
- ``dbh_threshold`` (float): DBH threshold in cm separating tall and small tree mortality (default: 15.0). Source: Vogt et al. 2014, dbh_h = 15 cm.
- ``mort_tall`` (float): mortality probability for trees with DBH >= threshold (default: 0.75). Source: Vogt et al. 2014, mort_tall = 0.75.
- ``mort_small`` (float): mortality probability for trees with DBH < threshold (default: 0.50). Source: Vogt et al. 2014, mort_small = 0.50.
- ``x_1``, ``x_2``, ``y_1``, ``y_2`` (float): domain bounds for patch placement (optional; derived from plant positions if omitted).
- ``verbose`` (bool): enable debug output (default: False).

# References

<a href="https://doi.org/10.1016/j.ecocom.2014.09.008" target="_blank">Vogt et al., 2014</a>

# Author(s)

Guanzhen Liu

# See Also

`pyMANGA.DisturbanceLib`, `pyMANGA.DisturbanceLib.Lightning`
