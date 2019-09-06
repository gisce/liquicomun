from .ree import REEformat

def REE_perd_name(subsystem):
    """
    Auxilar method to reach the expected REE perdidas string depending on the requested subsystem.

    Peninsular files use "perd" string, all others subsystems use "Sperd".
    """
    return {
        'peninsula': 'perd',
        #'BALEARES: 'S', 'CANARIAS', 'S', ...
    }.get(subsystem, 'Sperd')

# REE subsystems name //not performed automatically to be able to change it easily if REE change the codes
REE_subsystems_name = {
    'peninsula': '',            # default "fake" subsystem for peninsular data
    'baleares': 'BALEARES',
    'canarias': 'CANARIAS',
    'ceuta': 'CEUTA',
    'melilla': 'MELILLA',
}

# Equivalences between tariffs labels and the REE filenames
tariff_to_REEtariff = {
    '2.0A': '20A',
    '2.0DHA': '20D',
    '2.0DHS': '20DHS',
    '2.1A': '21A',
    '2.1DHA': '21D',
    '2.1DHS': '21DHS',
    '3.0A': '30A',
    '3.1A': '31A',
    '3.1A LB': '31A',
    '6.1A': 'g61A',
    '6.1B': 'g61B',
    '6.2': 'g62',
    '6.3': 'g63',
    '6.4': 'g64',
}


class Perdida(REEformat):
    """
    Initializes a Perdida from a set of conditions

    It downloads the related LIQUICOMUN and try to find the requested file inside the zip calling based on the REEformat flow.

    Accept a filename or:
    - tariff
    - date_start
    - date_end
    - subsystem (optional)
    - version (optional)
    """
    def __init__(self, filename=None, **request):
        # Default values if not provided
        version = "A1"
        subsystem = 'peninsula'

        if filename:
            filename_list = filename.split("_")
            assert len(filename_list) > 1 and filename_list[1], "Filename '{}' is not valid".format(filename)
            tariff = filename_list[1]
            date_start = filename_list[-1]
            date_end = filename_list[-2]
            version = filename_list[1]

            subsystem = ''
            if tariff.startswith("Sperd"):
                subsystem = filename_list[2]

            REEfile = tariff + subsystem

        else:
            # If no filename is provided, expect reach tariff, date_start and date_end
            assert "tariff" in request and request['tariff'] and type(request['tariff']) == str
            assert "date_start" in request and request['date_start'] and type(request['date_start']) == str
            assert "date_end" in request and request['date_end'] and type(request['date_end']) == str

            # Try to convert the humanized tariff to REE name
            try:
                tariff = tariff_to_REEtariff[request['tariff']]
            except:
                tariff = request['tariff']

            date_start = request['date_start']
            date_end = request['date_end']

            # Optional version
            if "version" in request:
                assert request['version'] and type(request['version']) == str
                version = request['version']

            # Optional subsystem. By default none (peninsula)
            subsystem_REE = ""
            if "subsystem" in request and request['subsystem'] != "peninsula":
                assert  request['subsystem'] and type(request['subsystem']) == str
                subsystem = request['subsystem']
                subsystem_REE = "_{}".format(REE_subsystems_name[subsystem])

            REEfile = REE_perd_name(subsystem) + tariff + subsystem_REE

            filename = "{version}_{REEfile}_{date_start}_{date_end}".format(
                version=version,
                REEfile=REEfile,
                date_start=date_start,
                date_end=date_end,
            )

        # Set main fields that describes the instance
        self.date_start = date_start
        self.date_end = date_end
        self.tariff = tariff
        self.version = version
        self.subsystem = subsystem
        self.name = REEfile
        self.file_tmpl = REEfile

        super(Perdida, self).__init__(filename=filename)


class Perdidas():
    """
    Perdidas class, provide an iterable way to fetch all available losses between a range of dates.
    """
    def __init__(self, date_start, date_end, tariffs=None, subsystems=None):
        """
        Initializes the Perdidas instance with the start and ending date.

        Perdidas is an iterable object that dumps their related Perdida instances based on the requested scenario (dates, tariffs and subsystems).

        Optionally,
        - can retreive for the passed list of tariffs
        - can retreive for the passed list of subsystems
        """

        self.date_start = date_start
        self.date_end = date_end

        available_tariffs = list(tariff_to_REEtariff.keys())
        if tariffs:
            # Assert that all passed tariffs exist
            assert all(x in available_tariffs for x in tariffs)
            self.tariffs = tariffs
        else:
            self.tariffs = available_tariffs

        available_subsystems = list(REE_subsystems_name.keys())
        if subsystems:
            # Assert that all passed subsystems exist
            assert all(x in available_subsystems for x in subsystems)

            self.subsystems = subsystems
        else:
            self.subsystems = available_subsystems


    def __iter__(self):
        """
        Initialize the iteration of tariffs and subsystems
        """
        self.current_subsystem = 0
        self.current_tariff = 0
        return self

    def next(self):
        """
        next method for py2 compat
        """
        return self.__next__()

    def __next__(self):
        """
        Next magic method to process the following element (from the scope of tariffs and subsystems)
        """
        # If tariff out of scope, go to the next subsystem
        if self.current_tariff >= len(self.tariffs):
            self.current_subsystem += 1
            self.current_tariff = 0

        # If subsystem out of scope, stop iteration
        if self.current_subsystem >= len(self.subsystems):
            raise StopIteration

        # Prepare the Loss for the current iteration
        current_params = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'tariff': self.tariffs[self.current_tariff],
            'subsystem': self.subsystems[self.current_subsystem],
        }

        current_loss = Perdida(**current_params)

        # Prepare the next iteration
        self.current_tariff += 1
        return current_loss
