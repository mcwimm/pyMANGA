# Description

This module manages the disturbance regime in a pyMANGA simulation.
It loads and coordinates one or more disturbance concepts and applies them sequentially at each timestep, in the order they appear in the project file.

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

# Author(s)

Guanzhen Liu
