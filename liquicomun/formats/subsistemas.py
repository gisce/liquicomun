from .perdidas import *

"""
Proporciona todos los posibles subsistemas
"""

class SubsistemaBase(REEformat):
    def __init__(self, token=None, version=None):
        token = '67c6aff80ca331eec78e1f62b7ffc6799e2674d82d57c04104a612db43496db3'

        expected_file = 'A2_Sperd20A_BALEARES_20171101_20171130' 1
        self.file_tmpl = self.name

        super(SubsistemaBase, self).__init__(file=expected_file, token=token, version=version)

class SubsistemaPeninsula(SubsistemaBase):
    ''' Subsistema peninsula '''
    name = 'peninsula'
    file_tmpl = ''

    def __init__(self, token=None, version=None):
        super(SubsistemaPeninsula, self).__init__(token=token, version=version)

class SubsistemaBaleares(SubsistemaBase):
    ''' Subsistema baleares '''
    name = 'Sperd20A_BALEARES'

    def __init__(self, token=None, version=None):
        super(SubsistemaBaleares, self).__init__(token=token, version=version)

"""

available_subsystems = {
    'peninsula': SubsistemaPeninsula,
    'baleares': SubsistemaBaleares,
    'canarias': SubsistemaCanarias,
    'ceuta': SubsistemaCeuta,
    'melilla': SubsistemaMelilla,
}

class Subsistema(object):
    ''' A generic Subsistema class '''
    def __new__(self, subsistemas=None, token=None, version=None):
        assert type(subsistemas) in [list, str]
        subsistemas = list(subsistemas) # ensure to work with a list
        assert len(subsistemas) > 1

        for subsistema in subsistemas:
            try:
                # Return the class depending on the filename or raise an error if not matched
                assert tariff in available_perd_tariffs, "Losses for tariff '{}' not defined as available tariff type ('{}')".format(tariff, available_perd_tariffs.keys())
                loss_tariff = available_perd_tariffs[tariff]
            except:
                assert tariff in tariffs_to_losses, "Losses for tariff '{}' not defined as available tariff type ('{}')".format(tariff, tariffs_to_losses.keys())
                loss_tariff = available_perd_tariffs[tariffs_to_losses[tariff]]

        return loss_tariff(file=file, token=token, version=version)
"""
