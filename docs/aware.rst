Aware
=====

You can read upstream information about Aware sensors from
http://www.awareframework.com/sensors/ .  This page elaborates the
material found there, in particular how the `koota-server
<https://github.com/digitraceslab/koota-server/>`__ project processes
the data.  Still, most of this information could be a useful hints to
others using the Aware data.

You can find our previous information `on the koota-server wiki
<https://github.com/digitraceslab/koota-server/wiki/Aware#data-notes>`__,
but this information is now being moved here.

Section names in general correspond to the koota-server converter
name.

Standard columns
----------------

A simple converter that shows timestamp of every packet uploaded.

* ``time``: timestamp of the data within that packet.
* ``packet_time``: when the packet was uploaded.
* ``table``: the sensor name (one of the other names on this page).


AwareScreen
-----------

Screen status, a row generated for each observed event.

Android:

* ``time``: unixtime, time of observation.
* ``screen_status``: 0=off, 1=on, 2=locked, 3=unlocked

AwareBattery
------------

Android: one row for each observed event.  An event is, for example, a
change of current charge level.  This does not seem to be a
continually observed event.

* ``time``: unixtime, time of observation
* ``battery_status``
* ``battery_level``
* ...
