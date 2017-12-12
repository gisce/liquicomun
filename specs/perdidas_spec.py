# -*- coding: utf-8 -*-
from __future__ import (absolute_import)
import vcr

from dateutil import relativedelta
from datetime import datetime

import logging
import random

from liquicomun import *

# Activate DEBUG log level
logging.basicConfig(level=logging.ERROR)

fixtures_path = 'specs/fixtures/liquicomun/'

spec_VCR = vcr.VCR(
    record_mode='new_episodes',
    cassette_library_dir=fixtures_path
)

called = {
    "by_dict": {
        'tariff': '2.0A',
        'date_start': '20171001',
        'date_end': '20171031',
    },
    "by_filename": "C2_perd20A_20171001_20171031",
    "losses_by_dict": {
        'date_start': '20171001',
        'date_end': '20171031',
    },
}

# Flag to activate extended tests //test all subsystems for all months in current and previous year
DISABLE_EXTENDED_TESTS = True

months_list = range(1,13)
current_year = datetime.now().year

tariffs_list = ['2.0A', '2.0DHA', '2.0DHS', '2.1A', '2.1DHS', '2.1DHA', '3.0A', '3.1A', '6.1A', '6.1B', '6.2', '6.3', '6.4']
subsystems_list = ["peninsula", "baleares", "canarias", "ceuta", "melilla"]
years_list = range(current_year-2, current_year+1)

with description('A new'):
    with before.each:
        pass


    with context('Perdidas'):
        with context('iteration'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('losses_iteration.yaml'):
                    #formats.REEformat.clear_cache()
                    expected_count = len(tariffs_list) * len(subsystems_list)

                    losses = Perdidas(**called['losses_by_dict'])
                    for counter, a_loss in enumerate(losses):
                        print ("Testing {} {}".format(a_loss.subsystem, a_loss.tariff))

                    # Increase counter to keep same index (base 1 instead base 0)
                    counter += 1

                    assert expected_count == counter, "Incongruent count of elements while iterating losses [expected '{}' vs '{}']".format(expected_count, counter)


    with context('Perdida'):
        with context('download'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('losses.yaml'):
                    #formats.REEformat.clear_cache()
                    loss = Perdida(**called['by_dict'])
                    loss_using_file = Perdida(filename = called['by_filename'])
                    assert loss.matrix == loss_using_file.matrix, "Results must match calling it with an scenario or with a filename"

                    #formats.REEformat.clear_cache()
                    to_call_30A = dict(called['by_dict'])
                    to_call_30A['tariff'] = '3.0A'
                    loss_30A = Perdida(**to_call_30A)
                    assert loss.matrix != loss_30A.matrix, "Results must not be the same for 20A and 30A"

            with it('must be performed as expected if subsystem is provided'):
                with spec_VCR.use_cassette('losses.yaml'):
                    #formats.REEformat.clear_cache()
                    to_call_canarias = dict(called['by_dict'])
                    to_call_canarias['tariff'] = '3.0A'
                    to_call_canarias['subsystem'] = 'canarias'

                    to_call_baleares = dict(called['by_dict'])
                    to_call_baleares['tariff'] = '3.0A'
                    to_call_baleares['subsystem'] = 'baleares'

                    loss_canarias = Perdida(**to_call_canarias)
                    loss_baleares = Perdida(**to_call_baleares)
                    assert loss_baleares.matrix != loss_canarias.matrix, "Results must match calling it with an scenario or with a filename"

            with it('must be performed if we try some random subsystems for some random month of current year'):
                to_call = dict(called['by_dict'])
                to_call['tariff'] = '3.1A'

                count_of_elements_to_process = 5

                # Test retrieve all available coeficients for all subsystems and this year
                for _ in range(count_of_elements_to_process):
                    a_subsystem = random.choice(subsystems_list)
                    a_month = random.choice(months_list)
                    a_tariff = random.choice(tariffs_list)
                    a_year = random.choice(years_list)

                    a_month = "{:02d}".format(a_month)
                    to_call['subsystem'] = a_subsystem
                    print ("Testing {}/{} {}:{}".format(a_month, a_year, a_subsystem, a_tariff))

                    with spec_VCR.use_cassette('losses_{}_{}_{}.yaml'.format(a_year, a_subsystem, a_month)):
                        start_string = "{}{}01".format(a_year, a_month)
                        to_call['date_start'] = start_string

                        end_datetime = datetime.strptime(start_string, '%Y%m%d') + relativedelta.relativedelta(months=1) - relativedelta.relativedelta(days=1)
                        to_call['date_end'] = end_datetime.strftime("%Y%m%d")

                        start_string = "{}{}01".format(a_year, a_month)

                        end_datetime = datetime.strptime(start_string, '%Y%m%d') + relativedelta.relativedelta(months=1) - relativedelta.relativedelta(days=1)
                        to_call['date_end'] = end_datetime.strftime("%Y%m%d")

                        a_loss = Perdida(**to_call)
                        the_matrix = a_loss.matrix


        if not DISABLE_EXTENDED_TESTS:
            ## Disabled due to the high cost to download all the specs
            ### Save cassettes for those tests will create a huge repo
            ### Commented to provide a quick reactivation for local testing purposes

            with it('must be performed if we try all subsystems for current year'):
                to_call = dict(called['by_dict'])
                to_call['tariff'] = '3.1A'

                # Test retrieve all available coeficients for all subsystems and this year
                for a_subsystem in subsystems_list:
                    for a_month in months_list:
                        a_month = "{:02d}".format(a_month)
                        to_call['subsystem'] = a_subsystem
                        print ("Testing {} {}".format(a_month, a_subsystem))

                        with spec_VCR.use_cassette('losses_{}_{}_{}.yaml'.format(current_year, a_subsystem, a_month)):
                            start_string = "{}{}01".format(current_year, a_month)
                            to_call['date_start'] = start_string

                            end_datetime = datetime.strptime(start_string, '%Y%m%d') + relativedelta.relativedelta(months=1) - relativedelta.relativedelta(days=1)
                            to_call['date_end'] = end_datetime.strftime("%Y%m%d")

                            start_string = "{}{}01".format(current_year, a_month)


                            end_datetime = datetime.strptime(start_string, '%Y%m%d') + relativedelta.relativedelta(months=1) - relativedelta.relativedelta(days=1)
                            to_call['date_end'] = end_datetime.strftime("%Y%m%d")

                            a_loss = Perdida(**to_call)
                            the_matrix = a_loss.matrix

            with it('must be performed if we try all subsystems for past year'):
                to_call = dict(called['by_dict'])
                to_call['tariff'] = '2.0A'

                # Test retrieve all available coeficients for all subsystems and past year
                for a_subsystem in subsystems_list:
                    for a_month in months_list:
                        a_month = "{:02d}".format(a_month)
                        to_call['subsystem'] = a_subsystem
                        print ("Testing {} {}".format(a_month, a_subsystem))

                        cassete_file = 'losses_{}_{}_{}.yaml'.format(current_year-1, a_subsystem, a_month)
                        with spec_VCR.use_cassette(cassete_file):
                            start_string = "{}{}01".format(current_year - 1, a_month)
                            to_call['date_start'] = start_string

                            end_datetime = datetime.strptime(start_string, '%Y%m%d') + relativedelta.relativedelta(months=1) - relativedelta.relativedelta(days=1)
                            to_call['date_end'] = end_datetime.strftime("%Y%m%d")

                            a_loss = Perdida(**to_call)
                            the_matrix = a_loss.matrix
