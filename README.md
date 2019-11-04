## Simple laptimer

This is simple laptime-calculation CGI-script in python.

It reads input in format of [log-new.txt](log-new.txt).

To basic modes: 
1. Laptime, with one reader: New log-line -> new lap 
   - race starts at first read
2. Laptime2, similar as previous, but race starts at given start-time. 
2. Stagetime, with one reader at start and second at finish. Results may be limited to max-laps.

Some parameters will be available in [timer.html](timer.html) front-page.

Things still to be sorted [TODO.md](TODO.md)
