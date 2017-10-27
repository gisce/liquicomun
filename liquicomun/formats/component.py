import calendar
from datetime import datetime, date, timedelta
from liquicomun.datetime.season import last_sunday
from builtins import range

class Component(object):
    '''Component to calculate cost'''
    def __init__(self, data=None, version=None):
        if not data:
            data = datetime.today()
        if not isinstance(data, (datetime, date)):
            raise ValueError('Invalid date passed')
        if not version:
            version = data.strftime("%Y%m%d%H%M%S")

        self.year = data.year
        self.month = data.month
        self.matrix = []
        self.version = version

        monthdays = calendar.monthrange(self.year, self.month)[1]
        for day in range(0, monthdays):
            self.matrix.append([0 for d in range(0, 25)])

    def get_weekday(self, day):
        return calendar.weekday(self.year, self.month, day)

    @property
    def num_days(self):
        return len(self.matrix)

    @property
    def start_date(self):
        return datetime(self.year, self.month, 1, 0, 0, 0)

    @property
    def end_date(self):
        return datetime(self.year, self.month, self.num_days, 23, 0, 0)

    def get(self, day, hour):
        if day > self.num_days or hour > 25 or hour < 0:
            return False
        return self.matrix[day - 1][hour]

    def set(self, day, hour, value=0):
        if day > self.num_days or hour > 25 or hour < 0:
            return False
        self.matrix[day - 1][hour] = value
        return True

    def load(self, data):
        if len(data) != len(self.matrix):
            return False
        if len(data[0]) != len(self.matrix[0]):
            return False
        row_counter = 0
        for row in data:
            field_counter = 0
            for v in row:
                self.set(row_counter + 1, field_counter, v)
                field_counter += 1
            row_counter += 1
        return True

    def __operate(self, other, op='add'):

        if not isinstance(other, (int, float)):
            if self.num_days != other.num_days:
                return False
            if self.month != other.month or self.year!=other.year:
                return False
        c3 = Component(date(self.year, self.month, 1))
        row_counter = 0
        for row in self.matrix:
            field_counter = 0
            for v in row:
                self_value = self.get(row_counter + 1, field_counter)
                if not isinstance(other, (int, float)):
                    other_value = other.get(row_counter + 1, field_counter)
                else:
                    other_value = other

                if op in ['add', 'radd']:
                    res = self_value + other_value
                elif op in ['mul', 'rmul']:
                    res = self_value * other_value
                elif op in ['sub']:
                    res = self_value - other_value
                elif op in ['rsub']:
                    res = other_value - self_value

                c3.set(row_counter + 1, field_counter, res)
                field_counter += 1
            row_counter += 1

        return c3

    def __add__(self, other, op='add'):
        return self.__operate(other, op)

    def __radd__(self, other, op='radd'):
        return self.__operate(other, op)

    def __sub__(self, other, op='sub'):
        return self.__operate(other, op)

    def __rsub__(self, other, op='rsub'):
        return self.__operate(other, op)

    def __mul__(self, other, op='mul'):
        return self.__operate(other, op)

    def __rmul__(self, other, op='rmul'):
        return self.__operate(other, op)

    def __str__(self):
        return "[%s,\n %s]" % (self._str_head, self._str_data)

    def get_sub_component(self, start_day, end_day=None):
        '''Returns a partial component. Empties the not selected days'''
        if end_day is not None:
            if not isinstance(end_day, int):
                raise ValueError('End day must be an integer')
            if not (1 <= end_day <= self.end_date.day):
                raise ValueError('End day out of bounds')
            if end_day < start_day:
                raise ValueError('End day must be greater or equal than Start day')

        if not isinstance(start_day, int):
            raise ValueError('Start day must be an integer')
        if not (1 <= start_day <= self.end_date.day):
            raise ValueError('Start day out of bounds')

        empty_day = [0] * 25
        for day in range(0, start_day - 1):
            self.matrix[day] = empty_day
        if end_day is not None:
            for day in range(end_day, self.end_date.day):
                self.matrix[day] = empty_day
        return self

    @property
    def _str_head(self):
        return "'%s-%s', '%s'" % (self.start_date.strftime("%Y%m%d%H%M"),
                                  self.end_date.strftime("%Y%m%d%H%M"),
                                  self.version)

    @property
    def _str_data(self):
        str = ""
        pos = 0
        for d in self.matrix:
            fill = pos and ' ' or '['
            str += "%s['%02d', %s],\n" % (fill, pos + 1, self.matrix[pos])
            pos += 1
        str += "]"
        return str

    @property
    def total_sum(self):
        total = sum(self.matrix[0])
        for d in self.matrix[1:]:
            total += sum(d)

        return total

    def get_audit_data(self, start=False, end=False):
        '''Returns a list of component values in the format:
        [(YYYY-MM-DD HH, value), (YYYY-MM-DD HH), ..)]
        leap hour 25
        :param start: start_day (included)
        :param end: end_day (included)
        :return: [(YYYY-MM-DD HH, value), (YYYY-MM-DD HH), ..)]
        '''
        start_day = start or 1
        end_day = end or self.num_days
        audit_data = []
        for day in range(start_day - 1, end_day):
            leap_hours = 0
            if self.month == 3:
                leap_day = last_sunday(self.year, self.month)
                if day == leap_day:
                    leap_hours = -1
            elif self.month == 10:
                leap_day = last_sunday(self.year, self.month)
                if day == leap_day:
                    leap_hours = 1
            num_hours = 24 + leap_hours
            h = 0
            file_version = getattr(self, 'file_version', '')
            for data in self.matrix[day][:num_hours]:
                h += 1
                audit_data.append(
                    (
                        '{0:04d}-{1:02d}-{2:02d} {3:02d}'.format(
                            self.year, self.month, day + 1, h
                        ),
                        round(data, 6),
                        file_version,
                        ''
                    )
                )

        return audit_data
