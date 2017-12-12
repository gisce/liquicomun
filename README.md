# Liquicomun lib

It provides a simple interface to reach ESIOS Liquicomun data.

Handled data:
- Perdidas (losses)
- Precios (prices)

## Installation

```
pip install liquicomun
```

## Usage

### Fetch all available losses for a concrete date

It provides an iterator that handle all the available losses for the requested scenario.

Start and end dates are mandatory

Tariffs and subsystems list are optional, and override the default list of elements to process.

```
from liquicomun import Perdidas

scenario = {
    'date_start': '20171001',
    'date_end': '20171031',
    #'tariffs': ['2.0A'],                   # Optional tariffs list
    #'subsystems': ["baleares", "ceuta"],   # Optional subsystems list
}

losses = Perdidas(**scenario)

# Iterate losses
for a_loss in losses:
    current_tariff = a_loss.tariff
    current_subsystem = a_loss.subsystem
    data_matrix = a_loss.matrix

```
