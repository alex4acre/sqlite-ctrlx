from setuptools import setup

setup(
      name="sqlite-ctrlx",
      version="1.0.01",
      description="Simple SQLite database",
      author="A. Fouraker",
      install_requires = ['ctrlx-datalayer', 'ctrlx_fbs'],   
      packages=['app','helper'],
      # https://stackoverflow.com/questions/1612733/including-non-python-files-with-setup-py
      scripts=['main.py'],
      license="Copyright (c) 2020-2021 Bosch Rexroth AG, Licensed under MIT License"
 )
