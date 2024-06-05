# IOC-Cartographer_TLP-CLEAR
Open-source Python script for generating Hilbert-Curve heat maps of IPv4 space as well as domain tree graphs - similar to the command-and-control pattern research published on [SarlackLab C2 Tracking](https://abjuri5t.github.io/SarlackLab/).

The tool contains two main scripts: **IP-Map.py** and **Domain-Map.py**. Both scripts require a file name as their first argument - with that file being a list of IP addresses or domain names (see [example-IPs.list](https://raw.githubusercontent.com/Abjuri5t/IOC-Cartographer_TLP-CLEAR/main/example-IPs.list) and [example-Domains.list](https://raw.githubusercontent.com/Abjuri5t/IOC-Cartographer_TLP-CLEAR/main/example-Domains.list) for examples). The script IP-Map.py accepts a second, optional, argument referred to as "weight". Weight controls the intensity of color in the heatmap and it has a default value of 1.0.

- `python3 IP-Map.py example-IPs.list 0.5`
- `python3 Domain-Map.py example-Domains.list`
