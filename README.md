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

For each iteration it return the related `next` Perdida instance (loss).

Start and end dates are mandatory.

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
    data_version = a_loss.version

```

### Fetch just the losses for one tariff and subsystem

It return a Loss instance

The expected tariff, start and end dates are mandatory.

Subsystem and version are optional. If no subsystem is provided will fetch the peninsular data.

```
from liquicomun import Perdida

scenario = {
    'date_start': '20171001',
    'date_end': '20171031',
    'tariff': '2.0A',
    #'subsystem': "baleares",              # default "" -> peninsula
}

a_loss = Perdida(**scenario)

data_matrix = a_loss.matrix
data_version = a_loss.version
current_tariff = a_loss.tariff
current_subsystem = a_loss.subsystem

```
