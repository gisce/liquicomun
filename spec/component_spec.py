from __future__ import absolute_import

from expects.testing import failure
from expects import *

from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta
import json
import fnmatch
import os
import calendar

from builtins import range

import sys
sys.path.insert(0, '.')

from liquicomun import formats

def touch(filepath, hora):
    os.utime(filepath, (hora, hora))

with description('Creating a component'):
    with context('If no params is given'):
        with it("has month and year as today's year and month"):
            c = formats.Component()
            assert c.year == datetime.today().year
            assert c.month == datetime.today().month

        with it("has 25 coef in every matrix row"):
            c = formats.Component()
            for day in c.matrix:
                assert len(day) == 25
        with it("has now version string"):
            c = formats.Component()
            assert c.version == datetime.now().strftime('%Y%m%d%H%M%S')

with description('REE components download'):
    with context('Inexistent file'):
        with before.all:
            ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
            self.token = ESIOS_TOKEN
        with it('should fail if no token passed'):
            today = date.today()
            numdays = calendar.monthrange(today.year, today.month)[1]
            ym = '%4d%02d' % (today.year, today.month)
            filename = 'C2_prmncur_%(ym)s01_%(ym)s%(numdays)s' % locals()
            expect(lambda: formats.Prmncur(filename)).to(raise_error(ValueError, 'No ESIOS Token'))

        with it('should download it'):
            next_month = date.today() + timedelta(days=30)
            numdays = calendar.monthrange(next_month.year, next_month.month)[1]
            ym = '%4d%02d' % (next_month.year, next_month.month)
            filename = 'A1_perd20A_%(ym)s01_%(ym)s%(numdays)s' % locals()
            p = formats.Perd20A(filename, self.token)
            assert p.start_date == datetime(next_month.year, next_month.month, 1)
            assert p.name == 'perd20A'

        with it('should fail if file not available yet'):
            today = date.today() + timedelta(days=428)
            numdays = calendar.monthrange(today.year, today.month)[1]
            ym = '%4d%02d' % (today.year, today.month)
            filename = 'C2_prmncur_%(ym)s01_%(ym)s%(numdays)s' % locals()
            expect(lambda: formats.Prmncur(filename, self.token)).to(raise_error(ValueError, 'Coeficients from REE not found'))

        with it('should fail if coeficients in file not available yet'):
            today = date.today() + timedelta(days=31)
            numdays = calendar.monthrange(today.year, today.month)[1]
            ym = '%4d%02d' % (today.year, today.month)
            filename = 'A1_prmncur_%(ym)s01_%(ym)s%(numdays)s' % locals()
            expect(lambda: formats.Prmncur(filename, self.token)).to(raise_error(ValueError, 'Coeficients from REE not found'))

    with context('Clear Cache'):
        with it('should clear cache only prefix C7 and everything'):
            directory = formats.REEformat._CACHE_DIR
            formats.REEformat.clear_cache()
            for num in range(1, 10):
                f = open('%sC%s_ree_123457890' % (directory, num,), 'w')
                f.write('GISCE')
                f.close()
            formats.REEformat.clear_cache('C7')
            for filename in os.listdir(directory):
                assert filename != 'C7_ree_1234567890'
            formats.REEformat.clear_cache()
            for filename in os.listdir(directory):
                assert not fnmatch.fnmatch(filename, '[CA][1-5]_*[0189]')

    with context('Better component and caching'):
            with it('should download A1 for today'):
                today = date.today()
                numdays = calendar.monthrange(today.year, today.month)[1]
                ym = '%4d%02d' % (today.year, today.month)
                filename = 'A1_perd20A_%(ym)s01_%(ym)s%(numdays)s' % locals()
                res1 = formats.Perd20A(filename, self.token)
                res2 = formats.Perd20A(filename, self.token)
                assert res1.file_version in ('A1', 'A2')
                assert res2.file_version in ('A1', 'A2')
                assert res1.origin == 'server'
                assert res2.origin == 'server'

            with it('should download A2 for before yesterday'):
                filedate = date.today() - timedelta(days=2)
                numdays = calendar.monthrange(filedate.year, filedate.month)[1]
                ym = '%4d%02d' % (filedate.year, filedate.month)
                filename = 'A1_perd20A_%(ym)s01_%(ym)s%(numdays)s' % locals()
                res = formats.Perd20A(filename, self.token)
                assert res.file_version in ('A2', 'A1')

            with it('should download C2 for 3 months ago'):
                formats.REEformat.clear_cache()
                filedate = date.today() - relativedelta(months=3)
                numdays = calendar.monthrange(filedate.year, filedate.month)[1]
                ym = '%4d%02d' % (filedate.year, filedate.month)
                filename = 'A1_perd20A_%(ym)s01_%(ym)s%(numdays)s' % locals()
                res1 = formats.Perd20A(filename, self.token)
                res2 = formats.Perd20A(filename, self.token)
                assert res1.file_version in ('A3', 'C2')
                assert res2.file_version in ('A3', 'C2')
                assert res1.origin == 'server'
                assert res2.origin == 'cache'

            with it('should download formats.Prmncur C2 for 2 months ago'):
                formats.REEformat.clear_cache()
                filedate = date.today() - relativedelta(months=2)
                numdays = calendar.monthrange(filedate.year, filedate.month)[1]
                ym = '%4d%02d' % (filedate.year, filedate.month)
                filename = 'A1_prmncur_%(ym)s01_%(ym)s%(numdays)s' % locals()
                res1 = formats.Prmncur(filename, self.token)
                res2 = formats.Prmncur(filename, self.token)
                assert res1.origin == 'server'
                assert res2.origin == 'cache'
                assert res1.file_version in ('C2')
                assert res2.file_version in ('C2')

            with it('should download C5 or C6 for 1 year ago'):
                formats.REEformat.clear_cache()
                filedate = date.today() - relativedelta(years=1)
                numdays = calendar.monthrange(filedate.year, filedate.month)[1]
                ym = '%4d%02d' % (filedate.year, filedate.month)
                filename = 'A1_prmncur_%(ym)s01_%(ym)s%(numdays)s' % locals()
                res1 = formats.Prmncur(filename, self.token)
                res2 = formats.Prmncur(filename, self.token)
                assert res1.origin == 'server'
                assert res2.origin == 'cache'
                assert res1.file_version in ('C5', 'C6')
                assert res2.file_version in ('C5', 'C6')


with description('formats.Perd20A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C3_perd20A_20141001_20141031'):
        with before.all:
            self.p = formats.Perd20A(self.data_path + 'C3_perd20A_20141001_20141031', token=self.token)

        with it('should be year 2014'):
            assert self.p.year == 2014
        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150917110842'):
            print (self.p.version, 20150917110842)
            assert self.p.version == '20150917110842'

        with it('has 18.0 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.0

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd21A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C3_perd21A_20141001_20141031'):
        with before.all:
            self.p = formats.Perd21A(self.data_path + 'C3_perd21A_20141001_20141031', token=self.token)

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150917110849'):
            print (self.p.version, 20150917110849)
            assert self.p.version == '20150917110849'

        with it('has 18.0 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.0

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd20DH component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C3_perd20D_20141001_20141031'):
        with before.all:
            self.p = formats.Perd20DH(self.data_path + 'C3_perd20D_20141001_20141031', token=self.token)
        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150917110844'):
            print (self.p.version, 20150917110844)
            assert self.p.version == '20150917110844'

        with it('has 13.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 13.8

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd21DH component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C3_perd21D_20141001_20141031'):
        with before.all:
            self.p = formats.Perd21DH(self.data_path + 'C3_perd21D_20141001_20141031', token=self.token)

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150917110853'):
            print (self.p.version, 20150917110853)
            assert self.p.version == '20150917110853'

        with it('has 13.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 13.8

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd20DHS component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C3_perd20DHS_20141001_20141031'):
        with before.all:
            self.p = formats.Perd20DHS(self.data_path + 'C3_perd20DHS_20141001_20141031', token=self.token)

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150917110846'):
            print (self.p.version, 20150917110846)
            assert self.p.version == '20150917110846'

        with it('has 18.5 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.5

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd21DHS component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C3_perd21DHS_20141001_20141031'):
        with before.all:
            self.p = formats.Perd21DHS(self.data_path + 'C3_perd21DHS_20141001_20141031', token=self.token)

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150917110855'):
            print (self.p.version, 20150917110855)
            assert self.p.version == '20150917110855'

        with it('has 18.5 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.5

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd30A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C3_perd30A_20141001_20141031'):
        with before.all:
            self.p = formats.Perd30A(self.data_path + 'C3_perd30A_20141001_20141031', token=self.token)

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150917110858'):
            print (self.p.version, 20150917110858)
            assert self.p.version == '20150917110858'

        with it('has 18.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 18.8

        with it('shoult not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

with description('Perd31A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C3_perd31A_20141001_20141031'):
        with before.all:
            self.p = formats.Perd31A(self.data_path + 'C3_perd31A_20141001_20141031', token=self.token)

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150917110900'):
            print (self.p.version, 20150917110900)
            assert self.p.version == '20150917110900'

        with it('has 8.5 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 8.5

        with it('should not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3


with description('Perd61 component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C3_perdg61_20141001_20141031'):
        with before.all:
            self.p = formats.Perd61(self.data_path + 'C3_perdg61_20141001_20141031', token=self.token)

        with it('should be year 2014'):
            assert self.p.year == 2014

        with it('should be month 10'):
            assert self.p.month == 10

        with it('should be 31 days'):
            assert len(self.p.matrix) == 31

        with it('has version 20150917110903'):
            print (self.p.version, 20150917110903)
            assert self.p.version == '20150917110903'

        with it('has 8.1 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 8.1

        with it('should not be 0.0 in Day 26 hour 24 (leap hour)'):
            assert self.p.get(26, 24) != 0.0

        with it('should return tuesday (3) on Day 16'):
            assert self.p.get_weekday(16) == 3

"""
with description('Perd61A component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C2_perdg61A_20160901_20160930'):
        with before.all:
            self.p = formats.Perd61A(self.data_path + 'C2_perdg61A_20160901_20160930', token=self.token)

        with it('should be year 2015'):
            assert self.p.year == 2015

        with it('should be month 09'):
            assert self.p.month == 9

        with it('should be 30 days'):
            assert len(self.p.matrix) == 30

        with it('has version 20150917110900'):
            print (self.p.version, 20150917110900)
            assert self.p.version == '20150917110900'

        with it('has 6.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 6.8

        with it('should return wednesday (2) on Day 16'):
            assert self.p.get_weekday(16) == 2

with description('Perd61B component from esios'):
    with before.all:
        self.data_path = './spec/pool/data/'
        ESIOS_TOKEN = os.getenv('ESIOS_TOKEN')
        self.token = ESIOS_TOKEN

    with context('C2_perdg61B_20160901_20160930'):
        with before.all:
            self.p = formats.Perd61B(self.data_path + 'C2_perdg61B_20160901_20160930', token=self.token)

        with it('should be year 2015'):
            assert self.p.year == 2015

        with it('should be month 09'):
            assert self.p.month == 9

        with it('should be 30 days'):
            assert len(self.p.matrix) == 30

        with it('has version 20150917110903'):
            print (self.p.version, 20150917110903)
            assert self.p.version == '20150917110903'

        with it('has 6.8 in Day 10 hour 10'):
            assert self.p.get(10, 10) == 6.8

        with it('should return wednesday (2) on Day 16'):
            assert self.p.get_weekday(16) == 2

"""
