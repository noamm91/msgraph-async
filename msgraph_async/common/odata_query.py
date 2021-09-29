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
    STARTS_WITH = 7, "startswith({attribute}, '{val}')"
    ENDS_WITH = 8, "endswith({attribute}, '{val}')"
    ANY_EQ = 9, "{attribute}/any(f:f/{inner_attribute} eq '{val}')"


class Order(int, Enum):
    asc = 1
    desc = 2


class LogicalConnector(int, Enum):
    AND = 1
    OR = 2


class Constrain:
    """
    Constrains is the building block that creates a Filter
    Each constrain is composed from 'attribute' (i.e. o365 resource supported attribute for filtering),
    'logical_operator' which specify the operation between the attribute and the value (e.g. equal) and a
    'value'.
    Constrain example for O365 message resource which has the attribute subject equals to "Trip Ahead" will be instanced
    like this: c = Constrain("subject", LogicalOperator.EQ, "Trip Ahead"
    """
    def __init__(self, attribute: str, logical_operator: LogicalOperator, value: str, inner_attribute: str = None):
        self.attribute = attribute
        self.logical_operator = logical_operator
        self.value = value
        self.inner_attribute = inner_attribute

    @property
    def attribute(self) -> str:
        return self._attribute

    @attribute.setter
    def attribute(self, val: str):
        if type(val) != str:
            raise ValueError("attribute must be string")
        self._attribute = val

    @property
    def logical_operator(self) -> LogicalOperator:
        return self._logical_operator

    @logical_operator.setter
    def logical_operator(self, val: LogicalOperator):
        if type(val) != LogicalOperator:
            raise ValueError("logical operator must be of type LogicalOperator")
        self._logical_operator = val

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, val: str):
        if type(val) != str:
            raise ValueError("value must be str")
        self._value = val

    @property
    def inner_attribute(self) -> str:
        return self._inner_attribute

    @inner_attribute.setter
    def inner_attribute(self, val: str):
        if val and type(val) != str:
            raise ValueError("inner attribute must be str")
        self._inner_attribute = val

    def __str__(self):
        return self._logical_operator.template.format(attribute=self._attribute, val=self._value,
                                                      inner_attribute=self._inner_attribute)


class Filter:
    def __init__(self, constrains: typing.List[Constrain], logical_connector: LogicalConnector = None):
        self.constrains = constrains
        self.logical_connector = logical_connector

    @property
    def constrains(self) -> typing.List[Constrain]:
        return self._constrains

    @constrains.setter
    def constrains(self, value):
        if type(value) is not list:
            raise ValueError("constrains must be list")
        for val in value:
            if type(val) is not Constrain:
                raise ValueError("all values must be constrains")
        self._constrains = value

    @property
    def logical_connector(self) -> LogicalConnector:
        return self._logical_connector

    @logical_connector.setter
    def logical_connector(self, value):
        if len(self.constrains) == 1:
            if value is not None:
                raise ValueError("logical connector has no meaning with single constrain")

        elif type(value) is not LogicalConnector:
            raise ValueError("logical connector must be of type LogicalConnector")

        self._logical_connector = value


class OrderBy:
    def __init__(self, attribute, order):
        self.attribute = attribute
        self.order = order

    @property
    def attribute(self) -> str:
        return self._attribute

    @attribute.setter
    def attribute(self, value: str):
        if type(value) is not str:
            raise ValueError("attribute must be string")
        self._attribute = value

    @property
    def order(self) -> Order:
        return self._order

    @order.setter
    def order(self, value: Order):
        if type(value) is not Order:
            raise ValueError("order must be of type Order")
        self._order = value

    def __str__(self):
        return f"{self.attribute} {self.order.name}"


class ODataQuery:
    def __init__(self):
        self._count = None
        self._expand = None
        self._filter = None
        self._select = None
        self._top = None
        self._order_by = None

    @property
    def count(self) -> bool:
        """Retrieves the total count of matching resources."""
        return self._count

    @count.setter
    def count(self, value: bool):
        if type(value) is not bool:
            raise ValueError("count must be boolean")
        self._count = value

    @property
    def expand(self) -> str:
        """Retrieves related resources."""
        return self._expand

    @expand.setter
    def expand(self, value: str):
        if type(value) is not str:
            raise ValueError("expand must be string")
        self._expand = value

    @property
    def filter(self) -> Filter:
        """Filters results (rows)."""
        return self._filter

    @filter.setter
    def filter(self, value: Filter):
        if type(value) is not Filter:
            raise ValueError("filter must of Filter type")
        self._filter = value

    @property
    def select(self) -> typing.List[str]:
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
    def top(self) -> int:
        """Sets the page size of results."""
        return self._top

    @top.setter
    def top(self, value: int):
        if type(value) is not int:
            raise ValueError("top must be integer")
        self._top = value

    @property
    def order_by(self) -> int:
        """Sets the field that will determine the order and the direction."""
        return self._order_by

    @order_by.setter
    def order_by(self, value: OrderBy):
        if type(value) is not OrderBy:
            raise ValueError("order_by must be OrderBy")
        self._order_by = value

    def _build_filter(self):
        res = ""
        for constrain in self.filter.constrains:  # type: Constrain
            if res:
                res += f" {self.filter.logical_connector.name.lower()} "
            res += str(constrain)
        return res

    def __str__(self):
        if not self.count and not self.expand and not self.filter and not self.select and not self.top:
            return "EMPTY OPEN DATA QUERY"
        res = []
        if self.count:
            res.append(f"$count={str(self.count).lower()}")
        if self.expand:
            res.append(f"$expand={self.expand.lower()}")
        if self.filter and self.filter.constrains:
            res.append(f"$filter={self._build_filter()}")
        if self.select:
            res.append(f"$select={','.join(self.select)}")
        if self.top:
            res.append(f"$top={str(self.top)}")
        if self.order_by:
            res.append(f"$orderby={str(self.order_by)}")

        return f"?{'&'.join(res)}"
