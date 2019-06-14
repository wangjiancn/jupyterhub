print('job start')
with open('/mnt/out_test.txt', 'w') as f:
    f.write('write some thing')
print('write finish')
from subprocess import check_output
print(check_output('pip list', shell=True))
