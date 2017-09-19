import re
import fnmatch
import os
from datetime import datetime, date, timedelta
from io import StringIO
from esios import Esios


from liquicomun import formats

class REEformat(formats.Component):
    ''' REE esios common format'''
    name = 'ree'
    file_tmpl = 'ree'
    filename = ''
    file_version = ''
    # May be 'cache', 'server' or 'file'
    file_origin = ''
    token = ''

    _CACHE_DIR = '/tmp/'

    version_order = (
        'C7', 'A7', 'C6', 'A6', 'C5', 'A5', 'C4', 'A4', 'C3', 'A3', 'C2',
        'A2', 'C1', 'A1'
    )
    no_cache = ('A2', 'C1', 'A1')

    def set_token(self, token):
        self.token = token

    def __init__(self, file=None, token=None):
        ''' Gets file from REE or disc and stores it in cache'''
        rows = []

        self.set_token(token)

        self.filename_re = '.+_%s(_2[0-9]{7}){2}$' % self.file_tmpl
        if not file:
            raise ValueError('No File')

        if not re.search(self.filename_re, file):
            raise ValueError('Bad %s file name' % self.name)

        self.filename = os.path.basename(file)

        if os.path.isfile(file):
            with open(file, 'rb') as csvfile:
                reereader = csv.reader(csvfile, delimiter=';')
                rows = [row for row in reereader]
                found_version = self.filename[:2]
                origin = 'file'
        else:
            found_version = ''
            for version in self.version_order:
                file = version + file[2:]
                self.filename = file
                if (os.path.isfile(self._CACHE_DIR + file)
                        and version not in self.no_cache):
                    with open(self._CACHE_DIR + file, 'rb') as csvfile:
                        found_version = version
                        reereader = csv.reader(csvfile, delimiter=';')
                        rows = [row for row in reereader]
                        origin = 'cache'
                        break
            if not found_version:
                rows = self.download(file)
                found_version = self.filename[:2]
                origin = 'server'

        self.file_version = found_version
        self.origin = origin
        self.loadfile(rows)

    @staticmethod
    def clear_cache(version=''):
        '''
        :param version: Cn or An prefix. All if empty
        :return: True or False
        '''
        if version:
            prefixes = [version]
        else:
            prefixes = list(REEformat.version_order)

        directory = REEformat._CACHE_DIR

        for filename in os.listdir(directory):
            for pfx in prefixes:
                if fnmatch.fnmatch(filename, '%s_*[0189]' % pfx):
                    os.unlink(directory + '/' + filename)

    def download(self, file):
        if not self.token:
            raise ValueError('No ESIOS Token')
        name = re.split('_', file)[-3]
        version = re.split('_', file)[-4]
        try:
            start_date = datetime.strptime(file[-17:-9], "%Y%m%d")
            end_date = datetime.strptime(file[-8:], "%Y%m%d")
            from esios import Esios
            #from esios.archives import Liquicomun

            e = Esios(self.token)
            zdata = e.liquicomun().download(start_date, end_date)
            if zdata:
                import zipfile
                c = StringIO(zdata)
                zf = zipfile.ZipFile(c)
                version = zf.namelist()[0][:2]
                file_dates = file[-17:]
                filename = '%(version)s_%(name)s_%(file_dates)s' % locals()
                try:
                    fdata = StringIO(zf.read(filename))
                    reereader = csv.reader(fdata, delimiter=';')
                    rows = [row for row in reereader]
                    f = open(self._CACHE_DIR + filename, 'w')
                    f.write(fdata.buf)
                    f.close()
                    self.filename = filename
                except KeyError:
                    raise ValueError('Coeficients from REE not found')
                finally:
                    zf.close()
            else:
                raise ValueError('Coeficients from REE not found')
        except Exception as e:
            raise ValueError('Coeficients from REE not found')

        return rows

    def check_data(self, rows):
        if not rows:
            raise ValueError('Empty File')
        # 2 header + 28-31 days + 1 footer = 31-34 rows
        if len(rows) not in [31, 32, 33, 34]:
            raise ValueError('Bad %s file format' % self.name)

        if len(rows[0]) < 2 or len(rows[0]) > 2 or not rows[0][0].startswith(self.name[:4]):
            raise ValueError('Bad %s file format' % self.name)

        if rows[-1][0] != '*':
            raise ValueError('Bad %s file format' % self.name)

    def format_data(self, rows):
        # formats data as 25 * num days matrix
        return [[v and float(v) or 0.0 for v in r[1:26]] for r in rows[2:-1]]

    def loadfile(self, rows):
        self.check_data(rows)

        version = ''.join(rows[1][:6])
        filedate = datetime.strptime(self.filename[-8:], '%Y%m%d')

        super(REEformat, self).__init__(data=filedate, version=version)
        data = self.format_data(rows)
        self.load(data)
