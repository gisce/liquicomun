import re
import fnmatch
import os
from datetime import datetime, date, timedelta
from io import BytesIO, StringIO, TextIOWrapper
from esios import Esios
import csv
import zipfile
import sys
import logging


from .component import Component

class REEformat(Component):
    ''' REE esios common format'''
    name = 'ree'
    file_tmpl = 'ree'
    file_name = ''
    file_version = ''
    # May be 'cache', 'server' or 'file'
    file_origin = ''
    token = ''

    _CACHE_DIR = '/tmp/'

    token = os.getenv('ESIOS_TOKEN')

    version_order = (
        'C7', 'A7', 'C6',
        #'A6', 'C5', 'C4', 'A5', 'A4',   #inconsistent formats see https://github.com/gisce/esios/pull/17
        'C3', 'A3', 'C2',
        'A2', 'C1', 'A1'
    )
    no_cache = ('A2', 'C1', 'A1')

    def set_token(self, token):
        self.token = token

    def __init__(self, filename=None):
        ''' Gets file from REE or disc and stores it in cache'''
        ''' If version is provided, ensure to fetch just this version '''
        rows = []

        self.file_name_re = '.+_%s(_2[0-9]{7}){2}$' % self.file_tmpl
        if not filename:
            raise ValueError('No File')

        if not re.search(self.file_name_re, filename):
            raise ValueError('Bad %s file name' % self.name)

        self.filename = os.path.basename(filename)

        available_versions = self.version_order
        if os.path.isfile(filename):
            with open(filename, 'rb') as csvfile:
                reereader = csv.reader(csvfile, delimiter=';')
                rows = [row for row in reereader]
                found_version = self.filename[:2]
                origin = 'file'
        else:
            found_version = ''
            for version in available_versions:
                filename = version + filename[2:]
                self.filename = filename
                if (os.path.isfile(self._CACHE_DIR + filename)
                        and version not in self.no_cache):
                    with open(self._CACHE_DIR + filename, 'r') as csvfile:
                        found_version = version
                        reereader = csv.reader(csvfile, delimiter=';')
                        rows = [row for row in reereader]
                        origin = 'cache'
                        break

            if not found_version:
                rows = self.download(filename)
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

        for file_name in os.listdir(directory):
            for pfx in prefixes:
                if fnmatch.fnmatch(file_name, '%s_*[0189]' % pfx):
                    os.unlink(directory + '/' + file_name)

    def download(self, filename):
        if not self.token:
            raise ValueError('No ESIOS Token')
        name = re.split('_', filename)[-3]
        version = re.split('_', filename)[-4]

        # Try to review all available versions //to set an iteriational limit
        count_of_versions = len(self.version_order)
        for current_version in range(count_of_versions):
            try:
                start_date = datetime.strptime(filename[-17:-9], "%Y%m%d")
                end_date = datetime.strptime(filename[-8:], "%Y%m%d")

                e = Esios(self.token)
                zdata = e.liquicomun().download(start_date, end_date, next=current_version)

                if zdata:
                    c = BytesIO(zdata)

                    with zipfile.ZipFile(c) as zf:
                        files_inside_zip = zf.namelist()

                        version = files_inside_zip[0][:2]
                        expected_filename = version + filename[2:]

                        try:
                            # Assert that the expected file is contained in the zip. If not raise to iterate the next
                            assert expected_filename in files_inside_zip, "File '{}' is not inside the zip".format(expected_filename)

                            zf.extractall("/tmp/liquicomun" + str(start_date))
                            # Open the needed file inside the Zip
                            with zf.open(expected_filename, "r") as fdata:
                                # Load the CSV
                                textfile = TextIOWrapper(fdata)
                                reereader = csv.reader(textfile, delimiter=';')

                                # Extract the rows list using the the csv reader
                                rows = [row for row in reereader]

                                # Extract current file to disk to keep a CACHE version
                                zf.extract(member=expected_filename, path=self._CACHE_DIR)

                                self.filename = expected_filename
                                return rows

                        except KeyError:
                            logging.debug ("Exception opening expected_filename '{}' inside zip".format(expected_filename))

                else:
                    logging.debug ("No valid data has been downloaded")

            except Exception as e:
                logging.debug ("Exception processing download [{}]".format(e))

        # If the iteration do not return anything for all available tests, rasise an error
        logging.error('Requested coeficients from REE not found for {}'.format(filename))
        raise ValueError('Requested coeficients from REE not found')

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
