from __future__ import absolute_import

from expects.testing import failure
from expects import *

from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta
import json
import fnmatch
import os

import sys
sys.path.insert(0, '.')

from liquicomun import formats

def touch(filepath, hora):
    os.utime(filepath, (hora, hora))


with description('Creating a component'):
    with context('If no params is given'):
        with it("has month and year as today's year and month"):
            c = Component()
            assert c.year == datetime.today().year
            assert c.month == datetime.today().month

        with it("has 25 coef in every matrix row"):
            c = Component()
            for day in c.matrix:
                assert len(day) == 25
        with it("has now version string"):
            c = Component()
            assert c.version == datetime.now().strftime('%Y%m%d%H%M%S')



with description('Perd20A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C3_perd20A_20141001_20141031'):
        with before.all:
            self.p = Perd20A(self.data_path + 'C3_perd20A_20141001_20141031')

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150121201650'):
            assert self.p.version == '20150121201650'

        with it('has 18.0 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.0

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd21A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C3_perd21A_20141001_20141031'):
        with before.all:
            self.p = Perd21A(self.data_path + 'C3_perd21A_20141001_20141031')

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150121201655'):
            assert self.p.version == '20150121201655'

        with it('has 18.0 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.0

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd20DH component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C3_perd20D_20141001_20141031'):
        with before.all:
            self.p = Perd20DH(self.data_path + 'C3_perd20D_20141001_20141031')

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150121201651'):
            assert self.p.version == '20150121201651'

        with it('has 13.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 13.8

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd21DH component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C3_perd21D_20141001_20141031'):
        with before.all:
            self.p = Perd21DH(self.data_path + 'C3_perd21D_20141001_20141031')

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150121201656'):
            assert self.p.version == '20150121201656'

        with it('has 13.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 13.8

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd20DHS component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C3_perd20DHS_20141001_20141031'):
        with before.all:
            self.p = Perd20DHS(self.data_path + 'C3_perd20DHS_20141001_20141031')

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150121201653'):
            assert self.p.version == '20150121201653'

        with it('has 18.5 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.5

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd21DHS component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C3_perd21DHS_20141001_20141031'):
        with before.all:
            self.p = Perd21DHS(self.data_path + 'C3_perd21DHS_20141001_20141031')

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150121201658'):
            assert self.p.version == '20150121201658'

        with it('has 18.5 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.5

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd30A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C3_perd30A_20141001_20141031'):
        with before.all:
            self.p = Perd30A(self.data_path + 'C3_perd30A_20141001_20141031')

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150121201700'):
            assert self.p.version == '20150121201700'

        with it('has 18.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.8

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd31A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C3_perd31A_20141001_20141031'):
        with before.all:
            self.p = Perd31A(self.data_path + 'C3_perd31A_20141001_20141031')

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150121201702'):
            assert self.p.version == '20150121201702'

        with it('has 8.5 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 8.5

        with it('should not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd61 component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C3_perdg61_20141001_20141031'):
        with before.all:
            self.p = Perd61(self.data_path + 'C3_perdg61_20141001_20141031')

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150121201703'):
            assert self.p.version == '20150121201703'

        with it('has 8.1 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 8.1

        with it('should not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd61A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C2_perdg61A_20150901_20150930'):
        with before.all:
            self.p = Perd61A(self.data_path + 'C2_perdg61A_20150901_20150930')

        with it('should be year 2015'):
            assert self.p.year == 2015

        with it('should be month 09'):
            assert self.p.month == 9

        with it('should be 30 days'):
            assert len(self.p.matrix) == 30

        with it('has version 20151008130816'):
            assert self.p.version == '20151008130816'

        with it('has 6.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 6.8

        with it('should return wednesday (2) on Day 16'):
            assert self.p.get_weekday(16) == 2

with description('Perd61B component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'

    with context('C2_perdg61B_20150901_20150930'):
        with before.all:
            self.p = Perd61B(self.data_path + 'C2_perdg61B_20150901_20150930')

        with it('should be year 2015'):
            assert self.p.year == 2015

        with it('should be month 09'):
            assert self.p.month == 9

        with it('should be 30 days'):
            assert len(self.p.matrix) == 30

        with it('has version 20151008130813'):
            assert self.p.version == '20151008130813'

        with it('has 6.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 6.8

        with it('should return wednesday (2) on Day 16'):
            assert self.p.get_weekday(16) == 2
