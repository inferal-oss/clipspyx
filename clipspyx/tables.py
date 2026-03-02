"""CLIPS 7.0 Deftable support.

This module is only functional when built against CLIPS 7.0+.

"""

import clipspyx

from clipspyx.modules import Module
from clipspyx.common import CLIPSError

from clipspyx._clipspyx import lib, ffi


class Deftable:
    """A Deftable represents a tabular data structure in CLIPS 7.0.

    In CLIPS, Deftables are defined via the (deftable) construct.

    """

    __slots__ = '_env', '_name'

    def __init__(self, env: ffi.CData, name: str):
        self._env = env
        self._name = name.encode()

    def __hash__(self):
        return hash(self._ptr())

    def __eq__(self, other):
        return self._ptr() == other._ptr()

    def __str__(self):
        string = lib.DeftablePPForm(self._ptr())
        string = ffi.string(string).decode() if string != ffi.NULL else ''

        return ' '.join(string.split())

    def __repr__(self):
        string = lib.DeftablePPForm(self._ptr())
        string = ffi.string(string).decode() if string != ffi.NULL else ''

        return "%s: %s" % (self.__class__.__name__, ' '.join(string.split()))

    def _ptr(self) -> ffi.CData:
        tbl = lib.FindDeftable(self._env, self._name)
        if tbl == ffi.NULL:
            raise CLIPSError(
                self._env, 'Deftable <%s> not defined' % self.name)

        return tbl

    @property
    def name(self) -> str:
        """Deftable name."""
        return self._name.decode()

    @property
    def module(self) -> Module:
        """The module in which the Deftable is defined."""
        name = ffi.string(lib.DeftableModule(self._ptr())).decode()

        return Module(self._env, name)

    @property
    def deletable(self) -> bool:
        """True if the Deftable can be undefined."""
        return lib.DeftableIsDeletable(self._ptr())

    @property
    def row_count(self) -> int:
        """The number of rows in the table."""
        return lib.DeftableRowCount(self._ptr())

    @property
    def column_count(self) -> int:
        """The number of columns in the table."""
        return lib.DeftableColumnCount(self._ptr())

    def lookup(self, row: int, column: int):
        """Look up a value in the table by row and column index.

        Row and column indices are 0-based.

        """
        value = ffi.new("UDFValue *")
        lib.GetTableValue(self._env, self._ptr(), row, column, value)

        return clipspyx.values.python_value(self._env, value)

    def undefine(self):
        """Undefine the Deftable.

        Equivalent to the CLIPS (undeftable) function.

        The object becomes unusable after this method has been called.

        """
        if not lib.Undeftable(self._ptr(), self._env):
            raise CLIPSError(self._env)


class Tables:
    """Deftable namespace class.

    .. note::

       All the Tables methods are accessible through the Environment class.

    """

    __slots__ = ['_env']

    def __init__(self, env):
        self._env = env

    def deftables(self) -> iter:
        """Iterate over the defined Deftables."""
        table = lib.GetNextDeftable(self._env, ffi.NULL)
        while table != ffi.NULL:
            name = ffi.string(lib.DeftableName(table)).decode()
            yield Deftable(self._env, name)

            table = lib.GetNextDeftable(self._env, table)

    def find_deftable(self, name: str) -> Deftable:
        """Find a Deftable by its name."""
        tbl = lib.FindDeftable(self._env, name.encode())
        if tbl == ffi.NULL:
            raise LookupError("Deftable '%s' not found" % name)

        return Deftable(self._env, name)
