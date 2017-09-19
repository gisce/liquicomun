from .ree import REEformat

class Perd20A(REEformat):
    ''' PERD20A from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perd20A'
    file_tmpl = 'perd20A'

    def __init__(self, file=None, token=None):
        super(Perd20A, self).__init__(file=file, token=token)


class Perd21A(REEformat):
    ''' PERD21A from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perd21A'
    file_tmpl = 'perd21A'

    def __init__(self, file=None, token=None):
        super(Perd21A, self).__init__(file=file, token=token)


class Perd20DH(REEformat):
    ''' PERD20DH from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perd20D'
    file_tmpl = 'perd20D'

    def __init__(self, file=None, token=None):
        super(Perd20DH, self).__init__(file=file, token=token)


class Perd21DH(REEformat):
    ''' PERD21DD from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perd21D'
    file_tmpl = 'perd21D'

    def __init__(self, file=None, token=None):
        super(Perd21DH, self).__init__(file=file, token=token)


class Perd20DHS(REEformat):
    ''' PERD20DHS from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perd20HS'
    file_tmpl = 'perd20DHS'

    def __init__(self, file=None, token=None):
        super(Perd20DHS, self).__init__(file=file, token=token)


class Perd21DHS(REEformat):
    ''' PERD21DHS from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perd21DHS'
    file_tmpl = 'perd21DHS'

    def __init__(self, file=None, token=None):
        super(Perd21DHS, self).__init__(file=file, token=token)


class Perd30A(REEformat):
    ''' PERD30A from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perd30A'
    file_tmpl = 'perd30A'

    def __init__(self, file=None, token=None):
        super(Perd30A, self).__init__(file=file, token=token)


class Perd31A(REEformat):
    ''' PERD31A from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perd31A'
    file_tmpl = 'perd31A'

    def __init__(self, file=None, token=None):
        super(Perd31A, self).__init__(file=file, token=token)

class Perd61(REEformat):
    ''' PERDG61 from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perdg61'
    file_tmpl = 'perdg61'

    def __init__(self, file=None, token=None):
        super(Perd61, self).__init__(file=file, token=token)

class Perd61A(REEformat):
    ''' PERDG61A from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perdg61A'
    file_tmpl = 'perdg61A'

    def __init__(self, file=None, token=None):
        super(Perd61A, self).__init__(file=file, token=token)

class Perd61B(REEformat):
    ''' PERDG61B from XN_liquicom_YYYYMM.zip esios file'''
    name = 'perdg61B'
    file_tmpl = 'perdg61B'

    def __init__(self, file=None, token=None):
        super(Perd61B, self).__init__(file=file, token=token)
