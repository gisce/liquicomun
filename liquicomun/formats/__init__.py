from .component import Component
from .perdidas import *
from .precios import *
from .ree import REEformat

tariffs_to_losses = {
    '2.0A': 'perd20A',
    '2.0DHA': 'perd20D',
    '2.0DHS': 'perd20DHS',
    '2.1A': 'perd21A',
    '2.1DHA': 'perd21D',
    '2.1DHS': 'perd21DHS',
    '3.0A': 'perd30A',
    '3.1A': 'perd31A',
    '6.1': 'perdg61',
    '6.1A': 'perdg61A',
    '6.1B': 'perdg61B',
}
