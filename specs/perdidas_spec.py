# -*- coding: utf-8 -*-
from __future__ import (absolute_import)
import vcr

from liquicomun import *

fixtures_path = 'specs/fixtures/liquicomun/'

spec_VCR = vcr.VCR(
    record_mode='new_episodes',
    cassette_library_dir=fixtures_path
)

with description('A new'):
    with before.each:
        pass
    with context('download'):
        with context('of losses'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('losses.yaml'):
                    formats.REEformat.clear_cache()
                    called = {
                        'tariff': '2.0A',
                        'date_start': '20171001',
                        'date_end': '20171031',
                    }
                    loss = Perdida(**called)
                    print (loss.matrix)