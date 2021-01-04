import re
import fnmatch
import os
from datetime import datetime
from io import BytesIO, TextIOWrapper
from esios import Esios
import csv
import time
import zipfile
import sys
import logging

from .component import Component


# https://www.boe.es/diario_boe/txt.php?id=BOE-A-2014-1052
LOSS_COEFF_BOE = {'20A': {'1': 14},
                  '20DH': {'1': 14.8, '3': 10.7},
                  '20DHS': {'1': 14.8, '2': 14.4, '3': 8.6},
                  '21A': {'1': 14},
                  '21DH': {'1': 14, '3': 10.7},
                  '21DHS': {'1': 14, '2': 14.4, '3': 8.6},
                  '30A': {'1': 15.3, '2': 14.6, '3': 10.7},
                  '31A': {'1': 6.6, '2': 6.4, '3': 4.8},
                  'g61A': {'1': 6.8, '2': 6.6, '3': 6.5, '4': 6.3, '5': 6.3, '6': 5.4},
                  'g61B': {'1': 6.8, '2': 6.6, '3': 6.5, '4': 6.3, '5': 6.3, '6': 5.4},
                  'g62': {'1': 4.9, '2': 4.7, '3': 4.6, '4': 4.4, '5': 4.4, '6': 3.8},
                  'g63': {'1': 3.4, '2': 3.3, '3': 3.2, '4': 3.1, '5': 3.1, '6': 2.7},
                  'g64': {'1': 1.8, '2': 1.7, '3': 1.7, '4': 1.7, '5': 1.7, '6': 1.4},
                  # https://www.boe.es/eli/es/cir/2020/01/15/3
                  '20TD': {'1': 16.7, '2': 16.3, '3': 18.0},
                  '30TD': {'1': 16.6, '2': 17.5, '3': 16.5, '4': 16.5, '5': 13.8, '6': 18.0},
                  '61TD': {'1': 6.7, '2': 6.8, '3': 6.5, '4': 6.5, '5': 4.3, '6': 7.7},
                  '62TD': {'1': 5.2, '2': 5.4, '3': 4.9, '4': 5.0, '5': 3.5, '6': 5.4},
                  '63TD': {'1': 4.2, '2': 4.3, '3': 4.0, '4': 4.0, '5': 3.0, '6': 4.4},
                  '64TD': {'1': 1.6, '2': 1.6, '3': 1.6, '4': 1.6, '5': 1.5, '6': 1.7},
                  '30TDVE': {'1': 16.6, '2': 17.5, '3': 16.5, '4': 16.5, '5': 13.8, '6': 18.0},
                  '61TDVE': {'1': 6.7, '2': 6.8, '3': 6.5, '4': 6.5, '5': 4.3, '6': 7.7}
                  }

# versions of ESIOS files with Kestimado
estimation_calculated = ['C2', 'A2', 'C1', 'A1']


class REEformat(Component):
    """ REE esios common format """
    name = 'ree'
    file_tmpl = 'ree'
    file_name = ''
    file_version = ''
    # May be 'cache', 'server' or 'file'
    file_origin = ''
    # token = ''

    _CACHE_DIR = '/tmp/'
    _CACHE_TIMEOUT = 3600

    token = os.getenv('ESIOS_TOKEN')

    version_order = (
        # real
        'C7', 'A7', 'C6',
        'A6', 'C5', 'C4', 'A5', 'A4',
        'C3', 'A3',
        # estimated
        'C2', 'A2', 'C1', 'A1'
    )

    no_cache = ('A2', 'C1', 'A1')

    def set_token(self, token):
        self.token = token

    def __init__(self, filename=None, k_table=None, tariff=None):
        """ Gets file from REE or disc and stores it in cache """
        """ If version is provided, ensure to fetch just this version """
        rows = []

        final_file_name = ''

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
                if k_table is not None:
                    if version in estimation_calculated:
                        filename = filename.replace('real', 'estimado')
                        self.name = self.name.replace('real', 'estimado')
                filename = version + filename[2:]
                self.filename = filename
                filepath = self._CACHE_DIR + filename
                if os.path.isfile(filepath):
                    file_age = time.time() - os.path.getmtime(filepath)
                    if version not in self.no_cache or file_age < self._CACHE_TIMEOUT:
                        with open(self._CACHE_DIR + filename, 'r') as csvfile:
                            found_version = version
                            if k_table is not None:
                                final_file_name = filename
                            reereader = csv.reader(csvfile, delimiter=';')
                            rows = [row for row in reereader]
                            origin = 'cache'
                            break

            if not found_version:
                if k_table is None:
                    rows = self.download(filename)
                else:
                    filename = filename.replace('estimado', 'real')
                    self.name = self.name.replace('estimado', 'real')
                    try:
                        rows = self.download_using_coeffs(filename)
                        final_file_name = self.filename
                    except ValueError:
                        print("No Kreal available. Switching to Kestimado.")
                        filename = filename.replace('real', 'estimado')
                        self.name = self.name.replace('real', 'estimado')
                        rows = self.download_using_coeffs(filename)
                        final_file_name = self.filename
                found_version = self.filename[:2]
                origin = 'server'

        self.file_version = found_version
        self.origin = origin

        if k_table is None:
            self.loadfile(rows)
        else:
            periodstable = []
            # periods table for current tariff
            if os.path.isfile(k_table):
                with open(k_table, 'rb') as csvfile:
                    reereader = csv.reader(csvfile, delimiter=';')
                    periodstable = [row for row in reereader]
            else:
                found_version = ''
                for version in available_versions:
                    k_table = version + k_table[2:]
                    if (os.path.isfile(self._CACHE_DIR + k_table)
                            and version not in self.no_cache):
                        with open(self._CACHE_DIR + k_table, 'r') as csvfile:
                            found_version = version
                            reereader = csv.reader(csvfile, delimiter=';')
                            periodstable = [row for row in reereader]
                            break

                if not found_version:
                    periodstable = self.download_using_coeffs(k_table)

            self.filename = final_file_name
            self.loadfile_using_coeffs(rows, periodstable, tariff)

    @staticmethod
    def clear_cache(version=''):
        """
        :param version: Cn or An prefix. All if empty
        :return: True or False
        """
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
                            assert expected_filename in files_inside_zip, "File '{}' is not inside the zip".format(
                                expected_filename)

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
                            logging.debug(
                                "Exception opening expected_filename '{}' inside zip".format(expected_filename))

                else:
                    logging.debug("No valid data has been downloaded")

            except Exception as e:
                logging.debug("Exception processing download [{}]".format(e))

        # If the iteration do not return anything for all available tests, rasise an error
        logging.error('Requested coeficients from REE not found for {}'.format(filename))
        raise ValueError('Requested coeficients from REE not found')

    def download_using_coeffs(self, filename):
        if not self.token:
            raise ValueError('No ESIOS Token')
        # name = re.split('_', filename)[-3]
        # version = re.split('_', filename)[-4]

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
                            assert expected_filename in files_inside_zip, "File '{}' is not inside the zip".format(
                                expected_filename)

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
                            logging.debug("Exception opening expected_filename '{}' inside zip".format(
                                expected_filename))

                else:
                    logging.debug("No valid data has been downloaded")

            except Exception as e:
                logging.debug("Exception processing download [{}]".format(e))

        # If the iteration do not return anything for all available tests, raise an error
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

    def check_data_using_coeffs(self, rows):
        self.check_data_without_file_name(rows)

        if len(rows[0]) < 2 or len(rows[0]) > 2 or not rows[0][0].startswith(self.name[:4]):
            raise ValueError('Bad %s file format' % self.name)

    def check_data_without_file_name(self, rows):
        if not rows:
            raise ValueError('Empty File')
        # 2 header + 28-31 days + 1 footer = 31-34 rows
        if len(rows) not in [31, 32, 33, 34]:
            raise ValueError('Bad %s file format' % self.name)

        if len(rows[0]) < 2 or len(rows[0]) > 2:
            raise ValueError('Bad %s file format' % self.name)

        if rows[-1][0] != '*':
            raise ValueError('Bad %s file format' % self.name)

    def format_data(self, rows):
        # formats data as 25 * num days matrix
        return [[v and float(v) or 0.0 for v in r[1:26]] for r in rows[2:-1]]

    def format_data_using_coeffs(self, rows, periodstable, tariff):
        # formats data as 25 * num days matrix
        matrix = []
        y = 1
        for r in rows[2:-1]:
            y += 1
            row = []
            x = 0
            for k in r[1:26]:
                x += 1
                period = periodstable[y][x]
                if period:
                    loss = k and float(k) * LOSS_COEFF_BOE[tariff][period]
                else:
                    loss = 0.0
                row.append(round(loss, 1) or 0.0)
            matrix.append(row)
        return matrix

    def loadfile(self, rows):
        self.check_data(rows)

        version = ''.join(rows[1][:6])
        filedate = datetime.strptime(self.filename[-8:], '%Y%m%d')

        super(REEformat, self).__init__(data=filedate, version=version)
        data = self.format_data(rows)
        self.load(data)

    def loadfile_using_coeffs(self, rows, periodstable, tariff):
        self.check_data_using_coeffs(rows)
        self.check_data_without_file_name(periodstable)

        version = ''.join(rows[1][:6])
        filedate = datetime.strptime(self.filename[-8:], '%Y%m%d')

        super(REEformat, self).__init__(data=filedate, version=version)
        data = self.format_data_using_coeffs(rows, periodstable, tariff)
        self.load(data)
