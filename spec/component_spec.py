from expects.testing import failure
from expects import *

from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import json
import fnmatch
import os

from liquicomun.formats import *

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
