# GeoRide Home assistant
![Logo GeoRide](https://brands.home-assistant.io/georide/logo.png)

⚠️ This is not an official implementation
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)

Official GeoRide website: https://georide.fr/

## Description
This component add some sensor for GeoRide Tracker

### What's entity is available :

    Get GeoRide position
    Get GeoRide lock status
    Change GeoRide lock status
    Add GeoRide from configuration.yml
    Add GeoRide from interface
    Get stollen status
    Get crashed status
    Get is owner status
    Get subsription status

### What's events are available:
you can filter by data.device_id == XX (XX is your tracker id)
you can display your tracker name by by data.device_name

event;
    
    georide_position_event
    georide_lock_event
    georide_device_event
    georide_alarm_event 

you can filter with data.type == 'alarm_vibration' to filter by vibration
here is the alarm type available: (listen the georide_alarm_event)

    alarm_vibration
    alarm_exitZone
    alarm_crash
    alarm_crashParking
    alarm_deviceOffline
    alarm_deviceOnline
    alarm_powerCut
    alarm_powerUncut
    alarm_batteryWarning
    alarm_temperatureWarning
    alarm_magnetOn
    alarm_magnetOff
    alarm_sonorAlarmOn

 
## Question:

### How to have the odometer in Km ?

Simply add a sensor like this in configuration.yaml
(Replace XX by your tracker id)

```yaml
sensor:
  - platform: template # Conversion georide de m en km
    sensors:
      odometer_XX_km:
        friendly_name: "Odometter - Km"
        value_template: "{{ states.sensor.odometer_XX.state | multiply(0.001) | round(3, 'flour') }}"
        unit_of_measurement: 'Km'


```

### How to use the event:

Simply made a automation like this:

```yaml
alias: '[TEST] Send notification'
description: ''
trigger:
  - platform: event
    event_type: georide_lock_event
condition: []
action:
  - service: notify.mobile_app_oneplus_a3003
    data:
      message: 'The device {{ data.device_name }} have recieved a lock event'
mode: single

```


## Options

| Name | Type | Requirement | `default` Description
| ---- | ---- | ------- | -----------
| email | string | **Required** | GeoRide email
| password | string | **Required** | GeoRide password


## Installation
### Option 1
- Just folow the integration config steps.

### Option 2
- Add the folowing line in your configuration.yml
```yaml
    georide:
        email: <your-email>@exmple.com
        password: <your-password>
```