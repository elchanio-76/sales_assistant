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

`scripts/document_db.sh`: uses eralchemy2 to extract ER diagram from database, then extracts ddl and feeds into claude for documentation. Output is saved in `docs/schema.md` and `docs/schema.png`.

### Migrations

Alembic is used for migrations. Check `pyproject.toml` for details of required packages.`
Autogenerate migrations from models using:

```bash
uv run alembic revision --autogenerate -m "message"
```

Then run migrations using:

```bash
uv run alembic upgrade head
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
