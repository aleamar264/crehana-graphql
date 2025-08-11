from datetime import datetime
from json import loads
from typing import Any

import icecream
from sqlalchemy.sql import operators
from sqlalchemy.sql.operators import Operators

operator_map = {
	"=": operators.eq,
	"!=": operators.ne,
	">": operators.gt,
	">=": operators.ge,
	"<": operators.lt,
	"<=": operators.le,
	"like": operators.like_op,
	"in": operators.in_op,
	"btw": operators.between_op,
}


def get_filters(filters: str, model_db: Any) -> tuple[Any] | tuple[Operators]:
	"""
	Convert a string of filters to a tuple with the real Operations.
	The operations available are:

		- =
		- !=
		- >
		- >=
		- <=
		- like
		- in
		- btw
	Args:
		filters (str): A string with `n` filters used in any operation in the db.
		model_db (Any): Model where the filter should be applied
	Returns:
		tuple[Any] | tuple[Operators] :A tuple with the applied filters.

	Examples:

	.. code-block:: python
		filter = "[["id", "=", 1]]"
		get_filters(filters=filter, model_db: Employee)"""
	filter_ = ()
	if not filters:
		return filter_

	filter_list: list[Any] = loads(filters)
	for column_name, operator, value in filter_list:
		# Handle dotted notation for relationships
		if "." in column_name:
			rel_name, sub_column = column_name.split(".", 1)
			rel_model = getattr(model_db, rel_name).property.mapper.class_
			column = getattr(rel_model, sub_column, None)
		else:
			column = getattr(model_db, column_name, None)

		if column is None:
			continue

		# Handle datetime conversion
		if isinstance(value, str) and operator in ["=", "!=", ">", ">=", "<", "<="]:
			try:
				value = datetime.strptime(value, "%Y-%m-%d")
			except ValueError:
				pass
		# Build filter expression
		if operator != "btw":
			filter_ += (operator_map[operator](column, value),)
		else:
			filter_ += (operator_map[operator](column, value[0], value[1]),)
		icecream.ic(filter_)
	return filter_
