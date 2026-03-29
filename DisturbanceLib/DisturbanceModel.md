# Description

This module manages the disturbance regime in a pyMANGA simulation.
It loads and coordinates one or more disturbance concepts (e.g. Hurricane, Lightning) and applies them sequentially at each timestep.

Disturbance concepts are specified as child tags within the `<disturbance>` block of the project file.
Each concept is dynamically loaded following pyMANGA's plugin convention (directory name == file name == class name).

The disturbance module is optional. Projects without a `<disturbance>` section run normally without any disturbances.

# Usage

```xml
<disturbance>
    <Hurricane>
        <!-- Hurricane parameters -->
    </Hurricane>
    <Lightning>
        <!-- Lightning parameters -->
    </Lightning>
</disturbance>
```

Multiple disturbance concepts can be combined in the same simulation (scenario 4 in Vogt et al. 2014).

# Available Concepts

- ``Hurricane``: Large-scale, patch-forming disturbance with DBH-dependent mortality.
- ``Lightning``: Small-scale, gap-forming disturbance with complete tree removal.

# References

<a href="https://doi.org/10.1016/j.ecocom.2014.09.008" target="_blank">Vogt et al., 2014</a>

# Author(s)

Guanzhen Liu

# See Also

`pyMANGA.DisturbanceLib.Hurricane`, `pyMANGA.DisturbanceLib.Lightning`
