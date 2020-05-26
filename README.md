# GeoRide Home assistant
![Logo GeoRide](https://brands.home-assistant.io/georide/logo.png)

⚠️ This is not an official implementation
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/gpl-3.0)

Official GeoRide website: https://georide.fr/

## Description
This component add some sensor for GeoRide Tracker


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