import db
import json
from math import ceil
from sys import argv

wagon_metadata = {}
locomotive_metadata = {}

def load_wagons():
    cur = db.conn.cursor()
    sql = 'select id, super_type, type, name, capacity, profit, cargo from wagon_types'
    cur.execute(sql)
    for res in cur.fetchall():
        wagon_info = {}
        wagon_info['super_type'] = res[1]
        wagon_info['type'] = res[2]
        wagon_info['name'] = res[3]
        wagon_info['capacity'] = res[4]
        wagon_info['profit'] = res[5]
        wagon_info['cargo'] = res[6]
        wagon_metadata[res[0]] = wagon_info

def load_locomotives():
    cur = db.conn.cursor()
    sql = 'select id, name, type, power, bonus_on, bonus from locomotive_types'
    cur.execute(sql)
    for res in cur.fetchall():
        info = {}
        info['name'] = res[1]
        info['type'] = res[2]
        info['power'] = res[3]
        info['bonus_on'] = res[4]
        info['bonus'] = res[5]
        locomotive_metadata[res[0]] = info

def load_metadata():
    db.open()
    load_wagons()
    load_locomotives()
    db.close()

def populate_trains_info(trains):
    all_trains = []
    for kee, val in trains.items():
        loco = {}
        loco = locomotive_metadata.get(kee[1]).copy()
        loco['id'] = kee[0]
        loco['operation'] = kee[2]
        wagons = []
        wagon_ids = {}
        for w in val:
            wagon_ids[w[1]] = wagon_ids.get(w[1], 0) + 1
        for wid, num in wagon_ids.items():
            this_wagon = wagon_metadata[wid].copy()
            this_wagon['count'] = num
            wagons.append(this_wagon)
        # print loco['name'], wagons
        train = {}
        train['locomotive'] = loco
        wagons = sorted(wagons, key = lambda x: (x['type']))
        train['wagons'] = wagons

        all_trains.append(train)
    all_trains = sorted(all_trains, key = lambda x: (x['locomotive']['operation'], x['locomotive']['id']))
    return all_trains

def get_trains(loco_id = None):
    db.open()
    cur = db.conn.cursor()
    trains_dict = {}
    sql = '''
        select l.id, l.locomotive_type_id, l.operation, w.id, w.wagon_type_id
          from wagons w,
               locomotives l
         where w.locomotive_id = l.id
         order by l.id, w.id
    '''
    cur.execute(sql)
    all_res = cur.fetchall()
    for res in all_res:
        if loco_id is not None:
            if loco_id != res[0]:
                continue
        loco = (res[0], res[1], str(res[2]))
        new_wagon = (res[3], res[4])
        wagons = trains_dict.get(loco, [])
        wagons.append(new_wagon)
        trains_dict[loco] = wagons
    db.close()
    return populate_trains_info(trains_dict)

def calculate_effective_payload(cargo, capacity, profit, apply_loco_bonus = False, loco_bonus = 0):
    payload = 0
    effective_payload = 0
    if cargo is not None:
        cargo = int(cargo)
        payload = 1 + cargo/100.0
        effective_payload = payload
        if apply_loco_bonus:
            effective_payload = payload*(1+(loco_bonus/100.0))
    else:
        payload = capacity
        effective_payload = int(ceil(capacity*(1+(profit/100.0))))
        if apply_loco_bonus:
            effective_payload += int(ceil(effective_payload*(loco_bonus/100.0)))
    return (payload, effective_payload)

def print_trains(trains):
    print "\n\ntrains"
    output = ""
    last_operation = ''
    overall_cargo = {}
    for train in trains:
        total_cargo = {}
        format_template = "{{:<{}}}"
        loco = train['locomotive']
        loco_operation = str(loco['operation'])
        loco_name = str(loco['name']) + '(' + str(loco.get('id', 0)) + ')'
        loco_bonus_on = str(loco.get('bonus_on', '') or '')
        loco_bonus_on = loco_bonus_on.split(',')
        loco_bonus = loco.get('bonus', 0) or 0
        loco_str_size = max(len(loco_name), len(str(loco['type'])), len(str(loco['power']))) + 5
        w_names = []
        w_types = []
        w_capacity = []
        w_sizes = []
        w_count = 0
        for wagon in train['wagons']:
            apply_loco_bonus = False
            w_count += wagon.get('count', 1)
            w_name = str(wagon['name']) + ' x ' + str(wagon.get('count', 1))
            w_names.append(w_name)
            w_type = str(wagon['type'])
            w_types.append(w_type)
            w_super_type = str(wagon.get('super_type', None))
            if w_super_type in loco_bonus_on:
                apply_loco_bonus = True
            cargo = wagon.get('cargo')
            capacity = wagon.get('capacity')
            profit = wagon.get('profit')
            payload, effective_payload = calculate_effective_payload(cargo, capacity, profit, apply_loco_bonus, loco_bonus)
            w_capacity.append(str(payload) + ' (' + str(effective_payload) + ')')
            total_cargo[w_type] = total_cargo.get(w_type, 0) + (effective_payload * wagon.get('count', 1))
            temp_storage = overall_cargo.get(loco_operation, {})
            temp_storage[w_type] = temp_storage.get(w_type, 0) + (effective_payload * wagon.get('count', 1))
            overall_cargo[loco_operation] = temp_storage
            # sizes of the strings for each wagon
            w_sizes.append(max(len(w_names[len(w_names)-1]), len(w_types[len(w_types)-1]), len(w_capacity[len(w_capacity)-1])) + 3)
        format_template *= len(w_names) + 1
        w_sizes = [25] * len(w_sizes)
        loco_str_size = 35
        format_template = format_template.format(loco_str_size, *w_sizes)

        if loco_operation != last_operation:
            output += '\n'*2 + loco_operation + ':\n'
            last_operation = loco_operation
        output += format_template.format(loco_name, *w_names) + '\n'
        output += format_template.format(loco['type'], *w_types) + '\n'
        output += format_template.format(str(w_count) + '/' + str(loco['power']), *w_capacity) + '\n'
        for kee, vaal in total_cargo.items():
            output += kee + ':' + str(vaal) + ', '
        output = output[0:len(output) - 2] + '\n'
        output += '\n'
    print output
    for pk, pv in overall_cargo.items():
        print pk, ':', pv

def print_wagons(wagons):
    print "\n\nWagons:"
    num_wagons_per_line = 5
    format_template = "{:<25}"
    wagons_by_type = {}
    for wagon in wagons:
        w_type = str(wagon["type"])
        this_wagons = wagons_by_type.get(w_type, list())
        this_wagons.append(wagon)
        wagons_by_type[w_type] = this_wagons

    for w_type, t_wagons in wagons_by_type.items():
        wagons_by_type[w_type] = sorted(t_wagons, key = lambda x: x["cargo"], reverse = True)

    for w_type, t_wagons in wagons_by_type.items():
        print w_type + ":"
        w_names = []
        w_cargos = []
        for wagon in t_wagons:
            w_names.append(str(wagon["name"]) + " x" + str(wagon["count"]))
            cargo = wagon["cargo"]
            capacity = wagon["capacity"]
            profit = wagon["profit"]
            payload, effective_payload = calculate_effective_payload(cargo, capacity, profit)
            payload_str = str(payload)
            if payload != effective_payload:
                payload_str += "(" + str(effective_payload) + ")"
            w_cargos.append(payload_str)
        print (format_template*len(t_wagons)).format(*w_names)
        print (format_template*len(t_wagons)).format(*w_cargos)
        print

def get_unused_wagons(wagon_type = None):
    sql = '''
        select wagon_type_id, count(1)
          from wagons
         where locomotive_id is null
         group by wagon_type_id
    '''
    wagons = []
    db.open()
    cur = db.conn.cursor()
    cur.execute(sql)
    for res in cur.fetchall():
        if wagon_type is not None:
            if wagon_type != str(wagon_metadata[res[0]]["type"]):
                continue
        wagon = wagon_metadata[res[0]].copy()
        wagon["count"] = res[1]
        wagons.append(wagon)
    db.close()
    return wagons

def get_unused_locos():
    sql = '''
        select id, locomotive_type_id
          from locomotives
         where id not in (
            select distinct(locomotive_id)
              from wagons
             where locomotive_id is not null);
    '''
    locos = []
    db.open()
    cur = db.conn.cursor()
    cur.execute(sql)
    for res in cur.fetchall():
        loco = locomotive_metadata[res[1]].copy()
        loco["id"] = res[0]
        locos.append(loco)
    db.close()
    return locos

def print_locos(locos):
    format_template = "{:<30}{:<10}{:<5}"
    print "\n\nLocomotives:"
    for loco in locos:
        name = loco["name"] + " (" + str(loco["id"]) + ")"
        print format_template.format(name, loco["type"], loco["power"])
    print "\n"

if __name__ == '__main__':
    load_metadata()
    inp = "all"
    if len(argv) > 1: inp = str(argv[1])

    if inp == "all":
        to_print = ["trains", "wagons", "locos"]
    else:
        to_print = list([inp])

    if "trains" in to_print:
        print_trains(get_trains())
    if "wagons" in to_print:
        print_wagons(get_unused_wagons())
    if "locos" in to_print:
        print_locos(get_unused_locos())
    # save_trains('new_trains.json', trains)
