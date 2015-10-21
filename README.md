##  A potential issue filtering by datetime field whilst using a Custom Type on Postgres

I'm using a TypeDecorator to enforce UTC timezoneaware datetimes, instead of using the standard DateTime type.

```[python]
class UTCDateTime(types.TypeDecorator):
    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(utc)

    def process_result_value(self, value, engine):
        if value is not None:
            return value.replace(tzinfo=utc)
``` 

This works with postgres when simply storing and accessing the datetime field.

However, it behaves unexpected when filtering on the datetime fild.

postgres version:  `PostgreSQL 9.4.5 on x86_64-apple-darwin14.5.0, compiled by Apple LLVM version 7.0.0 (clang-700.0.72), 64-bit`
sqlalchemy version: `1.0.9` with `psycopg2==2.6.1`

## In this repo
A script that adds a few rows to a table using the SQLalchemy type `DateTime` and a table using the custom type `UTCDateTime`

It then performs a `SELECT` `WHERE` the datetime filed is less than the value of another row.

This performs correctly using sqlite (you can switch to sqlite in the config file `hello.cfg`).

But using a postres database the filter does not perform as I would expect.


