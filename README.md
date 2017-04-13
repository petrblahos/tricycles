Authentication is hard, let's ride tricycles
============================================

The name's inspired by Chris McDonough's 
'''Authentication Is Hard, Let's Ride Bikes'''
https://github.com/mcdonc/bikes

The code is released under MIT license. It is meant to act as
an example and it should not be used in any real life application.
Your framework will do better job.

Setup
-----
You should install the bloody thing into a virtualenv:

  virtualenv -p python3 TRICYCLE
  cd TRICYCLE
  # in unix:
  . bin/activate.sh
  REM in windows:
  scripts\activate
  pip install pyramid
  pip install mako
  pip install waitress

  git clone https://github.com/petrblahos/tricycles.git
  cd tricycles
  python step01.py
  # or
  python step02.py
  # or so on

Remember that whenever you change the code you must restart the
application manually. All of the applications are single files.

step01
------
This is to show how to add a simple unsigned cookie to identify
the user. You can try
  document.cookie="userid=frank"
in Chrome's console to bypass any server-side authentication. You 
can also play about with max_age.

step02
------
The cookie now contains a digest, making it less easy to forge.
If you try changing cookie you will not get _authenticated_.

step03
------
Like step02 but raises a http exception instead of just saying nobody
is authenticated. The tricky part here is that we must effectively
log-out when raising the exception, otherwise we would get an exception
on every other request too.

Note that exceptions are actually requests, therefore we can manipulate
cookies on them.


