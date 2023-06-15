import os

with open("resourses.txt", "w") as output:
    os.chdir('extensions')
    files = [f for f in os.listdir()]
    for file in files:
        output.write(f'    <file alias="{file}">/resources/extensions/{file}</file>\n')
