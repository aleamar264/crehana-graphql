from collections.abc import Sequence
from typing import Any, Literal, TypeVar, override

from sqlalchemy import delete, func, lambda_stmt, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from utils.db.crud.entity import GeneralCrudAsync
from utils.exceptions import EntityDoesNotExistError

T = TypeVar("T")


class Repository(GeneralCrudAsync[T]):
	@override
	async def get_entity(
		self,
		db: AsyncSession,
		filter: tuple[Any],
	) -> Sequence[T]:
		"""Function that retrieves all the entities of a Model

		Args:
		db (AsyncSession): Async Session from the context o Dependencies.
		filter (tuple[Any]): Filter the data to get.

		Returns:
		Sequence[T]: Return the Sequence or List of data.

		.. code-block:: python

		# Graphql
		async def get_entity_graphql(info: strawberry.Info)-> Sequence[model]:
			await get_entity(info.context.db, filter=())
			filter_str = "[["id", "=", "1"]]"
			filter_: tuple[Operators] = get_filters(filter_str, model)
			await get_entity(info.context.db, filter=filter_)

		# FastApi endpoint
		@app.get("/")
		async def get_entity_fastapi(db: depend_db_annotated)-> Sequence[model]:
			await get_entity(db, filter=())
			filter_str = "[["id", "=", "1"]]"
			filter_: tuple[Operators] = get_filters(filter_str, model)
			await get_entity(db, filter=filter_)
		"""
		model = self.model
		stmt = lambda_stmt(lambda: select(model).filter(*filter))  # type: ignore
		result = await db.execute(stmt)
		return result.scalars().all()

	@override
	async def get_entity_pagination(
		self,
		db: AsyncSession,
		limit: int,
		offset: int,
		order_by: Literal["asc", "desc"],
		filter: tuple[Any],
		**kwargs,
	) -> tuple[Sequence[T], int]:
		"""Function that retrieves and paginates the entities of a Model

		Args:
			db (AsyncSession): Async Session from the context o Dependencie.
			limit (int): How many results want to retrieve
			offser (int): From which index return
			order_by (Literal ["asc", "desc"]): How the data should be ordered.
			filter (tuple[Any]): Filter the data to get.
			kwargs: Can be any statement that we want to run

		Returns:
			tuple[Sequence[T], int]: Return a tuple with the Sequence o List of the data, and the count of the data selected.

		.. code-block:: python

			# Graphql
			async def get_pagination_graphql(info: strawberry.Info)-> tuple[Sequence[model], int]:
				data, count = await get_entity_pagination(db=info.context.db, filter=(), limit=10, offset=0, order_by="asc")
				filter_str = "[["id", "=", "1"]]"
				filter_: tuple[Operators] = get_filters(filter_str, model)
				data, count = await get_entity_pagination(info.context.db, filter=filter_, limit=10, offset=0, order_by="asc")

			# FastApi endpoint
			@app.get("/")
			async def get_pagination_fastapi(db: depend_db_annotated)-> Sequence[model]:
				data, count = await get_entity_pagination(db=db, filter=(), limit=10, offset=0, order_by="asc",
					kwargs={"join": lambda s: s.join(model, model.id == model2.id)})
				filter_str = "[["id", "=", "1"]]"
				filter_: tuple[Operators] = get_filters(filter_str, model)
				data, count = await get_entity_pagination(db, filter=filter_, limit=10, offset=0, order_by="asc")
		"""
		model = self.model
		stmt = lambda_stmt(lambda: select(model))  # type: ignore
		if order_by == "desc":
			stmt += lambda s: s.order_by(model.id.desc())  # type: ignore
		elif order_by == "asc":
			stmt += lambda s: s.order_by(model.id.asc())  # type: ignore
		else:
			raise ValueError("Order by should be 'asc' or 'desc' ")

		stmt += lambda s: s.filter(*filter)  # type: ignore
		if kwargs:
			for v in kwargs.values():
				stmt += v
		count_query = lambda_stmt(
			lambda: select(func.count()).select_from(stmt.subquery())  # type: ignore
		)
		total_count = await db.scalar(count_query)

		stmt += lambda s: s.limit(limit)  # type: ignore
		stmt += lambda s: s.offset(offset)  # type: ignore
		result = await db.execute(stmt)
		return (result.scalars().all(), total_count)

	@override
	async def get_entity_by_id(self, entity_id: str | int, db: AsyncSession) -> T:
		"""Retrieves a single result from the Model

		Args:
		    db (AsyncSession): Async session from the context or dependencies.
		    entity_id (str | int): index or uuid4 from the entity to retrieve

		Returns:
		    T: Return the single result from the model.

		.. code-block:: python

		        # Graphql
		        async def get_entity_by_id_graphql(
		            info: strawberry.Info,
		        ) -> model:
		            await get_entity_by_id(
		                db=info.context.db,
		                entity=1,
		            )


		        # FastApi endpoint
		        @app.get("/")
		        async def get_entity_by_id_fastapi(
		            db: depend_db_annotated,
		        ) -> model:
		            await get_entity_by_id(
		                db=db,
		                entity=1,
		            )

		"""  # noqa: E101
		model = self.model
		stmt = lambda_stmt(lambda: select(model))  # type: ignore
		stmt += lambda s: s.where(model.id == entity_id)  # type: ignore
		result = await db.execute(stmt)
		if not (entity_result := result.scalar_one_or_none()):
			raise EntityDoesNotExistError(message="Entity don't exist")
		return entity_result

	@override
	async def delete_entity(
		self, entity_id: str | int, db: AsyncSession, filter: tuple[Any]
	) -> None:
		"""Function that deletes one entity.

		Args:
			db (AsyncSession): Async session from the context or dependencies..
			entity_id (str | int): index or uuid4 from the entity to retrieve
			filter (tuple[Any]): Filter the data to get.

		Returns:
			None

		.. code-block:: python

			# Graphql
			async def delete_entity_graphql(info: strawberry.Info)-> tuple[Sequence[model], int]:
				await delete_entity(db=info.context.db, filter=())
				filter_str = "[["email", "=", "somerandom@email.com"]]"
				filter_: tuple[Operators] = get_filters(filter_str, model)
				await delete_entity(info.context.db, filter=filter_)

			# FastApi endpoint
			@app.get("/")
			async def delete_entity_fastapi(db: depend_db_annotated)-> Sequence[model]:
				await delete_entity(db=db, filter=())
				filter_str = "[["email", "=", "somerandom@email.com"]]"
				filter_: tuple[Operators] = get_filters(filter_str, model)
				await delete_entity(db, filter=filter_)
		"""
		await self.get_entity_by_id(entity_id=entity_id, db=db)
		model = self.model
		stmt = lambda_stmt(lambda: delete(model))  # type: ignore
		stmt += lambda s: s.where(model.id == entity_id)  # type: ignore
		stmt += lambda s: s.filter(*filter)  # type: ignore
		if (await db.execute(stmt)).rowcount == 0:  # type: ignore
			raise EntityDoesNotExistError(
				message="Entity don't exist",
			)
		await db.commit()

	@override
	async def get_entity_by_args(
		self,
		column: InstrumentedAttribute[Any],
		entity_schema_value: Any,
		db: AsyncSession,
		filter: tuple[Any] | None = None,
	) -> T | None:
		"""Function that retrieves one entity, using any args.

		Args:
			db (AsyncSession): Async Session  from the context or dependencies.
			column (InstrumentedAttribute[Any]): A column from the model (that needs/is required) to be used for searching..
			entity_schema_value (Any): Can be any python variable like an int, str, so on ...
			filter (tuple[Any]): Filter the data to get.

		Returns:
			T | None: Can return the result of the entity, if it doesn't find anything, returns None.

		.. code-block:: python

			# Graphql
			async def get_entity_by_args_graphql(info: strawberry.Info)-> model | None:
				await get_entity_by_args(db=info.context.db, filter=(), column=model.id, entity_schema_value = 1)
				filter_str = "[["email", "=", "somerandom@email.com"]]"
				filter_: tuple[Operators] = get_filters(filter_str, model)
				await get_entity_by_args(info.context.db, filter=filter_, column=model.id, entity_schema_value = 1)

			# FastApi endpoint
			@app.get("/")
			async def  get_entity_by_args_fastapi(db: depend_db_annotated)-> model | None:
				await get_entity_by_args(db=db, filter=(), column=model.id, entity_schema_value = 1)
				filter_str = "[["email", "=", "somerandom@email.com"]]"
				filter_: tuple[Operators] = get_filters(filter_str, model)
				await get_entity_by_args(db, filter=filter_, column=model.id, entity_schema_value = 1)
		"""
		model = self.model
		stmt = lambda_stmt(lambda: select(model))  # type: ignore
		stmt += lambda s: s.where(column == entity_schema_value)  # type: ignore
		if filter:
			stmt += lambda s: s.filter(*filter)  # type: ignore
		result = await db.execute(stmt)
		if (entity_result := result.scalar_one_or_none()) is None:
			return None
		return entity_result

	@override
	async def create_entity(
		self,
		entity_schema: Any,
		db: AsyncSession,
	) -> T:
		"""Function that creates an entity.

		Args:
		    db (AsyncSession): Async Session from the Context or dependencies.
		    entity_schema (Any): A valid Pydantic Schema

		Returns:
		    T: Return the result of the entity.

		.. code-block:: python

		    # Graphql
		    async def create_entity_graphql(
		        info: strawberry.Info,
		    ) -> model:
		        schema: BaseModel = modelSchema(
		            ...
		        )
		        await create_entity(
		            db=info.context.db,
		            entity_schema=schema,
		        )


		    # FastApi endpoint
		    @app.get("/")
		    async def create_entity_args_fastapi(
		        db: depend_db_annotated,
		    ) -> model | None:
		        schema: BaseModel = modelSchema(
		            ...
		        )
		        await create_entity(
		            db=db,
		            entity_schema=schema,
		        )

		"""  # noqa: E101
		entity_result_ = entity_schema.model_dump()
		entity_result_ = self.model(**entity_result_)  # type: ignore
		db.add(entity_result_)  # type: ignore
		await db.commit()
		await db.refresh(entity_result_)  # type: ignore
		return entity_result_  # type: ignore

	@override
	async def update_entity(
		self,
		entity_id: int | str,
		entity_schema: dict[str, Any],
		db: AsyncSession,
		filter: tuple[Any] | None = None,
	) -> T:
		"""Function that updates an entity.

		Args:
		    db (AsyncSession): Async session from the context or dependencies.
		    entity_schema (dict[str, Any]): A valid Pydantic Schema already dump (converted to dict)
		    entity_id (int | str): id of the entity to update
		    filter (tuple[Any]):  Filter the data to get.

		Returns:
		    T: Return the result of the entity.

		.. code-block:: python

		    # Graphql
		    async def update_entity_graphql(info: strawberry.Info) -> model:
		        schema: BaseModel = modelSchema(...)
		        filter_str = "[["email", "=", "somerandom@email.com"]]"
		        filter_: tuple[Operators] = get_filters(filter_str, model)
		        await update_entity(db=info.context.db, entity_schema=schema.model_dump(), id=1, filter=filter_)


		    # FastApi endpoint
		    @app.get("/")
		    async def update_entity_fastapi(
		        db: depend_db_annotated,
		    ) -> model | None:
		        schema: BaseModel = modelSchema(...)
		        filter_str = "[["email", "=", "somerandom@email.com"]]"
		        filter_: tuple[Operators] = get_filters(filter_str, model)
		        await update_entity(db=db, entity_schema=schema.model_dump(), id=1, filter=filter_)

		"""  # noqa: E101
		model = self.model

		stmt = (
			update(model)  # type: ignore
			.where(model.id == entity_id)  # type: ignore
			.values(**entity_schema)
		)  # type: ignore
		if filter:
			stmt.filter(*filter)
		if (await db.execute(stmt)).rowcount == 0:  # type: ignore
			raise EntityDoesNotExistError(
				message="No record was updated; it may not exist or values may be the same.",
			) from None
		await db.commit()
		return await self.get_entity_by_id(entity_id, db)
