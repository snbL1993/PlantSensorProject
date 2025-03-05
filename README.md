# PlatSensorProject

### Small project that uses bluetooth sensors to track watering of houseplants.

Uses Docker containers runing on a Raspberry Pi to host a small local site with some Plotly graphs to show some stats for my houseplants.

The poller uses the RPI bluetooth to connect to the MiFlora Plantsensors and saves the data in a PostgreSQL Database.

The page is then hosted with Flask and uses Plotly to visualize the data.
