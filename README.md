# Module 183 - DDoS Presentation Demonstration
## Setup
To set the project up clone it and install the required packages.
```bash
git clone https://github.com/x47base/simple-ddos-demonstration.git
cd simple-ddos-demonstration
python -m pip install -r .\\requirements.txt
```

## Test
First start the web application.
```bash
python ./webapp.py
```
Then launch the monitor application.
```bash
python ./monitor.py
```
And then start as often as needed the attack.py application to showcase an attack on the web application.
```bash
python ./attack.py
```
