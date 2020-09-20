[![License]][LICENSE.md]
[![Telegram]][Teletram join]
![build](https://github.com/fincubator/booker/workflows/build/badge.svg)
![pre-commit](https://github.com/fincubator/booker/workflows/pre-commit/badge.svg)
[![Code style: black]][black code style]

--------------------------------------------------------------------------------

[Booker][Teletram join] is a microservice coordinating and validating payment
gateways.

# Requirements
* [Docker] (19.03.11 tested)
* [Docker Compose] (1.25.4 tested)

# Installation in Docker
Install git, Docker, Docker Compose:
```bash
sudo apt install git docker.io docker-compose
```
Clone the repository:
```bash
git clone https://github.com/fincubator/booker
cd booker
```
Create configuration files from examples and fill it with your data
```bash
cp .env.example .env
cp gateways.yml.example gateways.yml
```

Start the services by running the command:
```bash
sudo docker-compose up
```

# Contributing
You can help by working on opened issues, fixing bugs, creating new features or
improving documentation.

Before contributing, please read [CONTRIBUTING.md] first.

# License
Booker is released under the GNU Affero General Public License v3.0. See
[LICENSE.md] for the full licensing condition.

[License]: https://img.shields.io/github/license/fincubator/payment-gateway
[LICENSE.md]: LICENSE.md
[CONTRIBUTING.md]: CONTRIBUTING.md
[Telegram]: https://img.shields.io/badge/Telegram-fincubator-blue?logo=telegram
[Teletram join]: https://t.me/fincubator
[Code style: black]: https://img.shields.io/badge/code%20style-black-000000.svg
[black code style]: https://github.com/psf/black
[Docker]: https://www.docker.com
[Docker Compose]: https://www.docker.com
