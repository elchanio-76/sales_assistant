# AI Sales Assistant

This is the REAMDE.md stub.

## Installation

Project is using uv to manage dependencies.

```bash
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Scripts

```bash
uv run  scripts/extract_ddl.py
```

extracts DDL from current database using sqlalchemy.

```bash
uv run app/models/database.py create_database
```

Creates database tables from models. Needs empty DB to be created first.
Database will be created according to the latest schema. Use `alembic stamp head` to stamp a new head after creating it, if you want to retain ORM functionality for further development.

`scripts/document_db.sh`: uses eralchemy2 to extract ER diagram from database, then extracts ddl and feeds into claude for documentation. Output is saved in `docs/schema.md` and `docs/schema.png`.

### Migrations

Alembic is used for migrations. Check `pyproject.toml` for details of required packages.`
Autogenerate migrations from models using:
**Note:** You need to add `enum34` to your requirements.txt in order to use enums in migrations.

```bash
alembic revision --autogenerate -m "message"
```

Then run migrations using:

```bash
alembic upgrade head
```

Downgrade using:

```bash
uv run alembic downgrade -1
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Version

- 0.0.1: Initial commit

## License

[MIT](https://choosealicense.com/licenses/mit/)
