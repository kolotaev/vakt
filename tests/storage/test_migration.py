from abc import abstractmethod
import pytest

from vakt.storage.migration import Migration, MigrationSet, Migrator


# SETUP

class MMigration(Migration):
    def __init__(self, db):
        self.db = db

    @property
    @abstractmethod
    def letter(self):
        pass

    def up(self):
        self.db['data'] += self.letter

    def down(self):
        self.db['data'] = self.db['data'].replace(self.letter, '')


class M1(MMigration):
    @property
    def order(self):
        return 1

    @property
    def letter(self):
        return 'A'


class M2(MMigration):
    @property
    def order(self):
        return 2

    @property
    def letter(self):
        return 'B'


class M3(MMigration):
    @property
    def order(self):
        return 3

    @property
    def letter(self):
        return 'C'


class MigrationsForString(MigrationSet):
    def __init__(self, db):
        self.db = db

    def migrations(self):
        return [
            M1(self.db),
            M2(self.db),
            M3(self.db),
        ]

    def save_applied_number(self, number):
        self.db['ver'] = number

    def last_applied(self):
        return self.db['ver']


# TESTS
@pytest.mark.parametrize('db, expect_data, expect_saved_version', [
    ({'data': '', 'ver': 0}, 'ABC', 3),
    ({'data': 'Foo', 'ver': 0}, 'FooABC', 3),
    ({'data': '', 'ver': 2}, 'C', 3),
    ({'data': '', 'ver': 3}, '', 3),
])
def test_migrator_up(db, expect_data, expect_saved_version):
    m = Migrator(MigrationsForString(db))
    m.up()
    assert expect_data == db['data']
    assert expect_saved_version == db['ver']


@pytest.mark.parametrize('db, expect_data, expect_saved_version, number', [
    ({'data': '', 'ver': 0}, 'A', 1, 1),
    ({'data': '', 'ver': 0}, 'C', 3, 3),
    ({'data': '', 'ver': 0}, '', 0, 5),
    ({'data': 'AB', 'ver': 2}, 'AB', 2, 1),
    ({'data': 'AB', 'ver': 2}, 'AB', 2, 2),
    ({'data': 'AB', 'ver': 2}, 'ABC', 3, 3),
    ({'data': 'ABC', 'ver': 3}, 'ABC', 3, 5),
])
def test_migrator_up_with_number(db, expect_data, expect_saved_version, number):
    m = Migrator(MigrationsForString(db))
    m.up(number)
    assert expect_data == db['data']
    assert expect_saved_version == db['ver']


@pytest.mark.parametrize('db, expect_data, expect_saved_version', [
    ({'data': 'ABC', 'ver': 3}, '', 0),
    ({'data': 'FooABC', 'ver': 3}, 'Foo', 0),
    ({'data': 'AB', 'ver': 2}, '', 0),
    ({'data': '', 'ver': 3}, '', 0),
])
def test_migrator_down(db, expect_data, expect_saved_version):
    m = Migrator(MigrationsForString(db))
    m.down()
    assert expect_data == db['data']
    assert expect_saved_version == db['ver']


@pytest.mark.parametrize('db, expect_data, expect_saved_version, number', [
    ({'data': 'A', 'ver': 1}, '', 0, 1),
    ({'data': 'ABC', 'ver': 3}, 'AB', 2, 3),
    ({'data': 'ABC', 'ver': 3}, 'ABC', 3, 5),
    ({'data': 'ABC', 'ver': 3}, 'AC', 1, 2),
    ({'data': 'ABC', 'ver': 3}, 'BC', 0, 1),
    ({'data': 'AB', 'ver': 2}, 'AB', 2, 3),
    ({'data': 'AB', 'ver': 2}, 'A', 1, 2),
    ({'data': 'AB', 'ver': 2}, 'B', 0, 1),
])
def test_migrator_down_with_number(db, expect_data, expect_saved_version, number):
    m = Migrator(MigrationsForString(db))
    m.down(number)
    assert expect_data == db['data']
    assert expect_saved_version == db['ver']
