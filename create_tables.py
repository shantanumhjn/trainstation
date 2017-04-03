import db

db.open()
cur = db.conn.cursor()

# list of tables
# wagon_types
# wagons
# locomotive_types
# locomotives

# locomotive types table
sql = '''
create table if not exists locomotive_types (
    id          integer primary key,
    type        text not null,
    name        text not null,
    power       integer,
    bonus_on    text,
    bonus       integer,
    constraint locomotive_types_uk unique (name)
)
'''
cur.execute(sql)

#locomotives table
sql = '''
create table if not exists locomotives (
    id                  integer primary key,
    locomotive_type_id  integer,
    operation           text default 'unused',
    constraint locomotives_fk1 foreign key (locomotive_type_id) references locomotive_types (id)
)
'''
cur.execute(sql)

# wagon type table
sql = '''
create table if not exists wagon_types (
    id          integer primary key,
    super_type  text not null,
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
    locomotive_id   integer,
    constraint wagons_fk1 foreign key (wagon_type_id) references wagon_types (id),
    constraint wagons_fk2 foreign key (locomotive_id) references locomotives (id)
)
'''
cur.execute(sql)


db.close()
