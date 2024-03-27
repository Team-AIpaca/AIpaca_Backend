# DataBase Information
Modify `db_config.sample.py` to include the correct database information, and rename the file to `db_config.py`.

# db_config.sample.py file contents
```python
db_config = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'db': 'db',
    'charset': 'utf8mb4'
}
```

* `host`: Database server address.
* `user`: Database user name.
* `password`: Password of the database `user`.
* `db`: Database name.
* `charset`: Database character encoding. The recommended value is `utf8mb4`, which must match the `charset` in the database.