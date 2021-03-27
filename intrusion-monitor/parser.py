import re
import pandas as pd

with open('test.log', 'r') as f:
	lines=f.readlines()

for l in lines:
	pattern = re.compile(r'\[[^\d]*(\d+)[^\d]*\]:\W')
	res = re.findall(pattern, l)
	print(res)
	print()
