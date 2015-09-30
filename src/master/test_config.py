#!/usr/bin/env python3

from config import Config

cfg1 = Config()
cfg2 = Config()

print(cfg1.get('home'))
print(cfg2.get('home'))

print('Set home to HOME on cfg1')
cfg1.set('home','HOME')
print('cfg1', cfg1.get('home'))
print('cfg2', cfg2.get('home'))

print('Set home to ASD on cfg2')
cfg2.set('home','ASD')
print('cfg1', cfg1.get('home'))
print('cfg2', cfg2.get('home'))

print('Starting cfg3')
cfg3 = Config()
print('cfg1', cfg1.get('home'))
print('cfg2', cfg2.get('home'))
print('cfg3', cfg3.get('home'))

print('Set home to REHOME on cfg3')
cfg2.set('home','REHOME')
print('cfg1', cfg1.get('home'))
print('cfg2', cfg2.get('home'))
print('cfg3', cfg3.get('home'))


cfg2.help('all')



