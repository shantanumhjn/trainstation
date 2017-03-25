import db

db.open()
cur = db.conn.cursor()

# wagon type table
sql = '''
create table if not exists wagon_types (
    id          integer primary key,
    type        text not null,
    name        text not null,
    capacity    integer,
    profit      integer,
    cargo       integer,
    constraint wagon_types_uk unique (name)
)
'''
cur.execute(sql)

# wagons table
sql = '''
create table if not exists wagons (
    id              integer primary key,
    wagon_type_id   integer,
    constraint wagons_fk1 foreign key (wagon_type_id) references wagon_types (id)
)
'''
cur.execute(sql)

# locomotive types table
sql = '''
create table if not exists locomotive_types (
    id          integer primary key,
    type        text not null,
    name        text not null,
    power       integer,
    constraint locomotive_types_uk unique (name)
)
'''
cur.execute(sql)

#locomotives table
sql = '''
create table if not exists locomotives (
    id                  integer primary key,
    locomotive_type_id  integer,
    constraint locomotives_fk1 foreign key (locomotive_type_id) references locomotive_types (id)
)
'''
cur.execute(sql)

# train types table
sql = '''
create table if not exists train_types (
    id      integer primary key,
    type    text
)
'''
cur.execute(sql)

# insert into train_types
sql = 'insert into train_types (id, type) values (?, ?)'
data = [(1,'local'), (2, 'international'), (3, 'depot')]
cur.executemany(sql, data)
db.commit()

# trains table
sql = '''
create table if not exists trains (
    locomotive_id   integer,
    wagon_id        integer,
    train_type      integer default 1,
    constraint trains_pk primary key (locomotive_id, wagon_id),
    constraint trains_fk1 foreign key (locomotive_id) references locomotives(id),
    constraint trains_fk2 foreign key (wagon_id) references wagons(id)
)
'''
cur.execute(sql)

db.close()
