# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from liquicomun import *
from mamba import before, context, description, it

import random


months_list = range(1, 13)
years_list = range(2020, 2021)

tariffs_list = ['2.0A', '2.0DHA', '2.0DHS',
                '2.1A', '2.1DHS', '2.1DHA',
                '3.0A',
                '3.1A', '3.1A LB',
                '6.1A', '6.2', '6.3', '6.4']

# https://www.boe.es/eli/es/cir/2020/01/15/3
td_tariffs_list = ['2.0TD', '3.0TD', '6.1TD', '6.2TD', '6.3TD', '6.4TD', '3.0TDVE', '6.1TDVE']

subsystems_list = ['peninsula', 'baleares', 'canarias', 'ceuta', 'melilla']

called = {
    "by_dict": {
        'tariff': '2.0A',
        'date_start': '20201001',
        'date_end': '20201031',
        'type_import': 'perd_files'
    },
    "losses_by_dict": {
        'tariffs': tariffs_list,
        'date_start': '20201001',
        'date_end': '20201031',
        'type_import': 'perd_files'
    },
    "losses_by_dict_TD": {
        'tariffs': td_tariffs_list,
        'date_start': '20210601',
        'date_end': '20210630',
        'type_import': 'perd_files'
    }
}

with description('A'):
    with before.each:
        pass

    with context('tariff losses iteration by tariff'):
        with it('must be performed as expected'):
            expected_count = len(tariffs_list) * len(subsystems_list)

            losses = Perdidas(**called['losses_by_dict'])
            for counter, a_loss in enumerate(losses, start=1):
                if a_loss is not None:
                    print("Testing {} {}".format(a_loss.subsystem, a_loss.tariff))
                else:
                    print("Losses file not available in ESIOS")

            assert expected_count == counter, \
                "Incongruent count of elements while iterating losses [expected '{}' vs '{}']".format(
                    expected_count, counter)

    with context('Tariff losses download'):
        with it('must be performed as expected'
                ):
            loss_20A = Perdida(**called['by_dict'])
            to_call_30A = dict(called['by_dict'])
            to_call_30A['tariff'] = '3.0A'
            loss_30A = Perdida(**to_call_30A)
            assert loss_20A.matrix != loss_30A.matrix, "Results must not be the same for 20A and 30A"

        with it('must be performed as expected if subsystem is provided'):
            to_call_canarias = dict(called['by_dict'])
            to_call_canarias['tariff'] = '3.0A'
            to_call_canarias['subsystem'] = 'canarias'

            to_call_baleares = dict(called['by_dict'])
            to_call_baleares['tariff'] = '3.0A'
            to_call_baleares['subsystem'] = 'baleares'

            loss_canarias = Perdida(**to_call_canarias)
            loss_baleares = Perdida(**to_call_baleares)

            assert loss_baleares.matrix != loss_canarias.matrix, \
                "Results must not be the same for different subsystems"

        with it('must be performed if we try some random subsystems for some random months of current year'):
            to_call = dict(called['by_dict'])
            to_call['tariff'] = '3.1A'

            count_of_elements_to_process = 5

            # Test retrieve all available coefficients for all subsystems and this year
            for _ in range(count_of_elements_to_process):
                a_subsystem = random.choice(subsystems_list)
                a_month = random.choice(months_list)
                a_tariff = random.choice(tariffs_list)
                a_year = random.choice(years_list)

                a_month = "{:02d}".format(a_month)
                to_call['subsystem'] = a_subsystem
                print("Testing {}/{} {} {}".format(a_month, a_year, a_subsystem, a_tariff))

                start_string = "{}{}01".format(a_year, a_month)
                to_call['date_start'] = start_string

                end_datetime = datetime.strptime(
                    start_string, '%Y%m%d') + relativedelta(months=1) - relativedelta(days=1)
                to_call['date_end'] = end_datetime.strftime("%Y%m%d")

                start_string = "{}{}01".format(a_year, a_month)

                end_datetime = datetime.strptime(
                    start_string, '%Y%m%d') + relativedelta(months=1) - relativedelta(days=1)
                to_call['date_end'] = end_datetime.strftime("%Y%m%d")

                a_loss = Perdida(**to_call)
                the_matrix = a_loss.matrix

        with it('must be performed if we try all subsystems for a year'):
            to_call = dict(called['by_dict'])
            to_call['tariff'] = '3.1A'
            a_year = random.choice(years_list)

            # Test retrieve all available coefficients for all subsystems and this year
            for a_subsystem in subsystems_list:
                for a_month in months_list:
                    a_month = "{:02d}".format(a_month)
                    to_call['subsystem'] = a_subsystem
                    print("Testing {}/{} {} {}".format(a_year, a_month, a_subsystem, to_call['tariff']))

                    start_string = "{}{}01".format(a_year, a_month)
                    to_call['date_start'] = start_string

                    end_datetime = datetime.strptime(
                        start_string, '%Y%m%d') + relativedelta(months=1) - relativedelta(days=1)
                    to_call['date_end'] = end_datetime.strftime("%Y%m%d")

                    start_string = "{}{}01".format(a_year, a_month)

                    end_datetime = datetime.strptime(
                        start_string, '%Y%m%d') + relativedelta(months=1) - relativedelta(days=1)
                    to_call['date_end'] = end_datetime.strftime("%Y%m%d")

                    a_loss = Perdida(**to_call)
                    the_matrix = a_loss.matrix

    with context('tariff losses iteration by TD tariff'):
        with it('must be performed as expected'):
            expected_count = len(td_tariffs_list) * len(subsystems_list)

            losses = Perdidas(**called['losses_by_dict_TD'])
            for counter, a_loss in enumerate(losses, start=1):
                if a_loss is not None:
                    print("Testing {} {}".format(a_loss.subsystem, a_loss.tariff))
                else:
                    print("Losses file not available in ESIOS")

            assert expected_count == counter, \
                "Incongruent count of elements while iterating losses [expected '{}' vs '{}']".format(
                    expected_count, counter)

    with context('TD tariff losses download'):
        with it('must be performed as expected'
                ):
            to_call_20TD = dict(called['by_dict'])
            to_call_20TD['tariff'] = '2.0TD'
            to_call_20TD['date_start'] = '20210601'
            to_call_20TD['date_end'] = '20210630'
            loss_20TD = Perdida(**to_call_20TD)
            to_call_30TD = dict(called['by_dict'])
            to_call_30TD['tariff'] = '3.0TD'
            to_call_30TD['date_start'] = '20210601'
            to_call_30TD['date_end'] = '20210630'
            loss_30TD = Perdida(**to_call_30TD)
            assert loss_20TD.matrix != loss_30TD.matrix, "Results must not be the same for 20TD and 30TD"

        with it('must be performed as expected if subsystem is provided'):
            to_call_canarias = dict(called['by_dict'])
            to_call_canarias['tariff'] = '3.0TD'
            to_call_canarias['date_start'] = '20210601'
            to_call_canarias['date_end'] = '20210630'
            to_call_canarias['subsystem'] = 'canarias'

            to_call_baleares = dict(called['by_dict'])
            to_call_baleares['tariff'] = '3.0TD'
            to_call_baleares['date_start'] = '20210601'
            to_call_baleares['date_end'] = '20210630'
            to_call_baleares['subsystem'] = 'baleares'

            loss_canarias = Perdida(**to_call_canarias)
            loss_baleares = Perdida(**to_call_baleares)

            assert loss_baleares.matrix != loss_canarias.matrix, \
                "Results must not be the same for different subsystems"

            formats.REEformat.clear_cache()
