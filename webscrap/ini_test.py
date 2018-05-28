import configparser
import time

config = configparser.ConfigParser()

config.add_section('section_a')
config.set('section_a', 'str_a', 'config val a')
config.set('section_a', 'str_b', 'config val b')
config.set('section_a', 'str_c', 'config val c')

with open('test.ini', 'w') as configfile:
    config.write(configfile)


config.read('test.ini')
print(config.get('section_a', 'str_a'))
print(config.get('section_a', 'str_b'))
print(config.get('section_a', 'str_c'))

    


while True:
    time.sleep(5)
    config.read('test.ini')
    print(config.get('section_a', 'str_c'));
