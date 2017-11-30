# -*- coding: utf-8 -*-
from __future__ import (absolute_import)
import vcr

from liquicomun import *

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
    "by_filename": "C2_perd20A_20171001_20171031"
}


with description('A new'):
    with before.each:
        pass
    with context('download'):
        with context('of losses'):
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
