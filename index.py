from Person import Person

drink_type = 'beer'
test_object = Person('male', 80, 3.5, drink_type)
result = test_object.start_calculating(20, 0.05)

print('Optimization with break times finished')
print('Matches: {}'.format(len(result['breaks_output'])))
for data in result['breaks_output']:
    print('EBAC: {}. Drinking plan {}'.format(data['ebac'], data['drinking_plan']))
print('-'*100)

print('Optimization with drink part finished')
print('Matches: {}'.format(len(result['drink_part_output'])))
for data in result['drink_part_output']:
    print('EBAC: {}. Drinking plan {}'.format(data['ebac'], data['drinking_plan']))
print('-'*100)

