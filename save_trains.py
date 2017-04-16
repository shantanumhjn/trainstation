from show_trains import *

def save_trains(file_name, trains):
    for train in trains:
        train['locomotive'].pop('bonus', None)
        train['locomotive'].pop('bonus_on', None)
        train['locomotive'].pop('id', None)
        for wagon in train['wagons']:
            wagon.pop('super_type', None)
    with open('data/' + file_name, 'w') as f:
        f.write(json.dumps(trains, indent = 2))

def save_wagons(file_name, wagons):
    for wagon in wagons:
        wagon.pop('super_type', None)
    with open("data/" + file_name, 'w') as f:
        f.write(json.dumps(wagons, indent = 2))

def save_locos(file_name, locos):
    for loco in locos:
        loco.pop('bonus', None)
        loco.pop('bonus_on', None)
        loco.pop('id', None)
    with open('data/' + file_name, 'w') as f:
        f.write(json.dumps(locos, indent = 2))

if __name__ == "__main__":
    load_metadata()
    # print len(get_trains())
    save_trains("all_trains.json", get_trains())
    save_wagons("all_unused_wagons.json", get_unused_wagons())
    save_locos("all_unused_locomotives.json", get_unused_locos())
