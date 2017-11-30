# -*- coding: utf-8 -*-
from __future__ import (absolute_import)
import vcr

from liquicomun import Perdidas
from liquicomun import SubsistemaBaleares

fixtures_path = 'specs/fixtures/liquicomun/'

spec_VCR = vcr.VCR(
    record_mode='new_episodes',
    cassette_library_dir=fixtures_path
)

with description('A new'):
    with before.each:
        pass
    with context('download'):
        with context('of losses by subsystem'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('losses-subsystem.yaml'):
                    a = SubsistemaBaleares()
