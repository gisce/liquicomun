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
    filename = ''
    file_version = ''
    # May be 'cache', 'server' or 'file'
    file_origin = ''
    token = ''

    _CACHE_DIR = '/tmp/'

    version_order = (
        'C7', 'A7', 'C6',
        #'A6', 'C5', 'C4', 'A5', 'A4',   #inconsistent formats see https://github.com/gisce/esios/pull/17
        'C3', 'A3', 'C2',
        'A2', 'C1', 'A1'
    )
    no_cache = ('A2', 'C1', 'A1')

    def set_token(self, token):
        self.token = token

    def __init__(self, file=None, token=None, version=None):
        ''' Gets file from REE or disc and stores it in cache'''
        ''' If version is provided, ensure to fetch just this version '''
        rows = []

        self.set_token(token)

        self.filename_re = '.+_%s(_2[0-9]{7}){2}$' % self.file_tmpl
        if not file:
            raise ValueError('No File')

        if not re.search(self.filename_re, file):
            print("File '{}' re '{}', result '{}'".format(file, self.filename_re,  re.search(self.filename_re, file)))
            raise ValueError('Bad %s file name' % self.name)

        self.filename = os.path.basename(file)

        available_versions = self.version_order
        # Handle available_versions overriding with str or list
        if False: #version:
            try:
                assert type(version) == list, "Version must be a string or a list"
                for element in version:
                    assert element in self.version_order, "One of provided element versions ['{}'] is not defined as available on ESIOS".format(element, self.version_order)
                available_versions = version

            except:
                assert type(version) == str, "Version must be a string or a list"
                assert version in self.version_order, "Provided version '{}' is not defined as available on ESIOS".format(version, self.version_order)
                available_versions = [version]

        if os.path.isfile(file):
            print("Entro isfile")
            with open(file, 'rb') as csvfile:
                reereader = csv.reader(csvfile, delimiter=';')
                rows = [row for row in reereader]
                found_version = self.filename[:2]
                origin = 'file'
        else:
            print("Entro available")
            found_version = ''
            for version in available_versions:
                file = version + file[2:]
                self.filename = file
                if (os.path.isfile(self._CACHE_DIR + file)
                        and version not in self.no_cache):
                    with open(self._CACHE_DIR + file, 'r') as csvfile:
                        found_version = version
                        reereader = csv.reader(csvfile, delimiter=';')
                        rows = [row for row in reereader]
                        origin = 'cache'
                        break

                print (version)

            if not found_version:
                print ("not found")
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

        print (file)
        if not self.token:
            raise ValueError('No ESIOS Token')
        name = re.split('_', file)[-3]
        version = re.split('_', file)[-4]

        try:
            start_date = datetime.strptime(file[-17:-9], "%Y%m%d")
            end_date = datetime.strptime(file[-8:], "%Y%m%d")

            e = Esios(self.token)
            zdata = e.liquicomun().download(start_date, end_date)

            if zdata:
                c = BytesIO(zdata)

                with zipfile.ZipFile(c) as zf:
                    version = zf.namelist()[0][:2]
                    filename = version + file[2:]

                    try:
                        zf.extractall("/tmp/liquicomun" + str(start_date))
                        # Open the needed file inside the Zip
                        with zf.open(filename, "r") as fdata:
                            # Load the CSV
                            textfile = TextIOWrapper(fdata)
                            reereader = csv.reader(textfile, delimiter=';')

                            # Extract the rows list using the the csv reader
                            rows = [row for row in reereader]

                            # Extract current file to disk to keep a CACHE version
                            zf.extract(member=filename, path=self._CACHE_DIR)

                    except KeyError:
                        logging.error ("Coeficients from REE not found, exception opening filename inside zip {}".format(filename))
                        raise ValueError('Coeficients from REE not found')
            else:
                logging.error ("Coeficients from REE not found, No available data has been downloaded".format())
                raise ValueError('Coeficients from REE not found')

        except Exception as e:
            logging.error ("Coeficients from REE not found, exception processing download")
            raise ValueError('Coeficients from REE not found')

        self.filename = filename
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
