from .ree import REEformat

class Grcosdnc(REEformat):
    """
    Componentes precio final por coste ajustes del sistema (EUR/MWh bc)
    Comercializadores libres y consumidores directos
    POS from XN_liquicom_YYYYMM.zip esios file
    """
    name = 'grcosdnc'
    file_tmpl = 'grcosdnc'

    def __init__(self, file=None, token=None):
        super(Grcosdnc, self).__init__(file=file, token=token)

    def check_data(self, rows):
        if not rows:
            raise ValueError('Empty File')
        # 2 header + n days * 24 (+/- 1 Leap hour) + 1 footer
        # (num_rows - 3) % 24 = 0 or 1 or 23
        # A1 has only partial days
        # 0: usually
        # 1: summer to winter
        # 23: winter to summer
        if ((len(rows) - 3) % 24) not in [0, 1, 23]:
            raise ValueError('Bad %s file format' % self.name)

        if len(rows[0]) < 2 or len(rows[0]) > 2 or not rows[0][0].startswith(self.name[:4]):
            raise ValueError('Bad %s file format' % self.name)

        if len(rows[2]) != 15:
            raise ValueError('Bad %s file format' % self.name)

        if rows[-1][0] != '*':
            raise ValueError('Bad %s file format' % self.name)

    def _get_day_hour(self, date_field):
        '''
        Returns day and hour of date_field
        :param date_field: date_fiel in format YYYYMM DD HH
        :return: (day, hour)
        '''
        date_row = date_field.split(' ')
        if len(date_row) < 2:
            return 0, 0
        return int(date_row[1]), int(date_row[2])

    def _get_value(self, pot, total):
        '''
        Returns total per hour. Its 'Coste Total' column
        adding 'Factor de potencia' column only when it's negative
        :param pot: 'Factor de Potencia' column value
        :param total: 'Coste Total' column value
        :return: Total as 'Coste Total' + 'Factor de potencia'
        '''
        potencia = float(pot or '0.0')
        if potencia < 0:
            extra = potencia * -1.0
        else:
            extra = 0.0
        return float(total) + float(extra)

    def format_data(self, rows):
        # formats data as 25 * num days matrix

        # date (YYYYMM DD HH) row[0]
        # Factor Potencia: row[12]
        # Total: row[13]

        monthdays = calendar.monthrange(self.year, self.month)[1]

        matrix = []
        for d in range(0, monthdays):
            matrix.append([0 for h in range(0, 25)])

        for row in rows[2:-1]:
            day, hour = self._get_day_hour(row[0])
            value = self._get_value(row[11], row[12])
            matrix[day - 1][hour - 1] = value

        return matrix


class Prmncur(REEformat):
    """
    Coste medio horario en el mercado de produccion (EUR/MWh BC)
    Comercializadores, excepto de ultimo recurso, y consumidores directos
    PMD + POS + PC3 from XN_liquicom_YYYYMM.zip esios file
    """
    name = 'prmncur'
    file_tmpl = 'prmncur'

    def __init__(self, file=None, token=None):
        super(Prmncur, self).__init__(file=file, token=token)


class Prmdiari(REEformat):
    """
    Precio del mercado diario (EUR/MWh)
    PMD from XN_liquicom_YYYYMM.zip esios file
    """
    name = 'prmdiari'
    file_tmpl = 'prmdiari'

    def __init__(self, file=None, token=None):
        super(Prmdiari, self).__init__(file=file, token=token)


class Prgpncur(REEformat):
    """
    Coste medio por pago por capacidad para demanda NO suministrada por CUR (EUR/MWh bc consumido)
    PC3 from XN_liquicom_YYYYMM.zip esios file
    """
    name = 'prgpncur'
    file_tmpl = 'prgpncur'

    def __init__(self, file=None, token=None):
        super(Prgpncur, self).__init__(file=file, token=token)
