pretix Screenshotting tool
--------------------------

Requirements:

* Chrome 60 or newer with headless support
* Python packages listed in requirements.txt

How to run:

* Go to pretix' ``src`` folder and execute ``python setup.py develop``
* Execute ``make production`` there
* Go back here and run ``PYTHONPATH=. py.test scenes``
