import typing
from enum import Enum


class LogicalOperator(int, Enum):

    def __new__(cls, value, template=None):
        logical_operator = int.__new__(cls, value)
        logical_operator._value_ = value
        logical_operator.template = template
        return logical_operator

    EQ = 1, "{attribute} eq {val}"
    NE = 2, "{attribute} ne {val}"
    LT = 3, "{attribute} lt {val}"
    GT = 4, "{attribute} gt {val}"
    LE = 5, "{attribute} le {val}"
    GE = 6, "{attribute} ge {val}"
    AND = 7, "{attribute} and {val}"
    OR = 8, "{attribute} or {val}"
    STARTS_WITH = 9, "startsWith({attribute}, {val})"
    ENDS_WITH = 10, "endsWith({attribute}, {val})"


class Constrain:

    def __init__(self, attribute, logical_operator: LogicalOperator, value: str):
        self._attribute = attribute
        self._logical_operator = logical_operator
        self._value = value

    def __str__(self):
        return self._logical_operator.template.format(attribute=self._attribute, val=self._value)


class ODataQuery:
    def __init__(self):
        self._count = None
        self._expand = None
        self._filter = None
        self._select = None
        self._top = None

    @property
    def count(self):
        """Retrieves the total count of matching resources."""
        return self._count

    @count.setter
    def count(self, value: bool):
        if type(value) is not bool:
            raise ValueError("count must be boolean")
        self._count = value

    @property
    def expand(self):
        """Retrieves related resources."""
        return self._expand

    @expand.setter
    def expand(self, value: str):
        if type(value) is not str:
            raise ValueError("expand must be string")
        self._expand = value

    @property
    def filter(self):
        """Filters results (rows)."""
        return self._filter

    @filter.setter
    def filter(self, value: typing.List[Constrain]):
        if type(value) is not list:
            raise ValueError("filter must be list of constrains")
        for val in value:
            if type(val) is not Constrain:
                raise ValueError("all values must be constrains")
        self._filter = value

    @property
    def select(self):
        """Filters properties (columns)."""
        return self._select

    @select.setter
    def select(self, value: typing.List[str]):
        if type(value) is not list:
            raise ValueError("select must be list of strings")
        for val in value:
            if type(val) is not str:
                raise ValueError("all values should be strings")
        self._select = value

    @property
    def top(self):
        """Sets the page size of results."""
        return self._top

    @top.setter
    def top(self, value: int):
        if type(value) is not int:
            raise ValueError("top must be integer")
        self._top = value

    def _build_filter(self):
        res = ""
        for constrain in self.filter:  # type: Constrain
            res += str(constrain) + " "
        return res[:-1]

    def __str__(self):
        if not self.count and not self.expand and not self.filter and not self.select and not self.top:
            return "EMPTY OPEN DATA QUERY"
        res = []
        if self.count:
            res.append(f"$count={str(self.count).lower()}")
        if self.expand:
            res.append(f"$expand={self.expand.lower()}")
        if self.filter:
            res.append(self._build_filter())
        if self.select:
            res.append(f"$select={','.join(self.select)}")
        if self.top:
            res.append(f"$top={str(self.top)}")

        return f"?{'&'.join(res)}"
