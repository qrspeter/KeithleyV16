# Diode and FET measurement with Keithley 2636b using LAN

Based on "Red Light Emitting Diode" from http://lampx.tugraz.at/~hadley/semi/studentreports/WS18/RedLED/RedLED.html
by TU Graz / Graz University of Technology


Recommendation for Windows users: to prevent searching for absent drivers install preliminary  KickStart-1.9.8 (by Keithley Instruments). KickStart installs the drives.

* KeithleyV15.py - KeithleyV15 library.
* diode_iv.py - IV measurement I(V). Several samples into one file.
* diode_it.py - I(t) at given U until break.
* diode_iv_t.py - I(t) measurement based on periodic IV measurements.
* photoresponces_measurement.py - measurement series of responces on pumpes
* photoresponces_analysis.py - calculating of photoresponces and conductivity decay times


/re-engineering/ - versions based on KeithleyV15 for re-engineering:
* diode_i_t_pulsed - I(t)  at given V with pulsed laser with delay and accumulation.  Several samples into one file.
* fet_output.py - output curve Ids(Vds) at given Vgs.
* fet_transfer - transfer curve Ids(Vgs) at given Vds.

Data are saved into ./data/ folder

Press Ctrl-C to exit from delay or accumulation loop

This work was supported by the Ministry of Science and Higher Education of the Russian Federation, goszаdanie no. 2019-1080.

International Research and Education Centre for Physics of Nanostructures, ITMO University, Saint Petersburg 197101, Russia