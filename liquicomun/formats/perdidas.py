from .ree import REEformat

def REE_perd_name(subsystem):
    return {
        'peninsula': 'perd',
        #'BALEARES: 'S', 'CANARIAS', 'S', ...
    }.get(subsystem, 'Sperd')


tariff_to_REEtariff = {
    '2.0A': '20A',
    '2.0DHA': '20D',
    '2.0DHS': '20DHS',
    '2.1A': '21A',
    '2.1DHA': '21D',
    '2.1DHS': '21DHS',
    '3.0A': '30A',
    '3.1A': '31A',
    '6.1': 'g61',
    '6.1A': 'g61A',
    '6.1B': 'g61B',
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
            version = filename_list[-1]

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
            if "subsystem" in request:
                assert  request['subsystem'] and type(request['subsystem']) == str
                subsystem = request['subsystem']

            REEfile = REE_perd_name(subsystem) + tariff

            filename = "{version}_{REEfile}_{date_start}_{date_end}".format(
                version=version,
                REEfile=REEfile,
                date_start=date_start,
                date_end=date_end,
            )

        # Set the name and file_tmpl needed for REEformat class
        self.name = REEfile
        self.file_tmpl = REEfile

        super(Perdida, self).__init__(filename=filename)
