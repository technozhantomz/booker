[![License]][LICENSE.md]
[![Telegram]][Teletram join]

--------------------------------------------------------------------------------

[Booker][Teletram join] is a microservice coordinating and validating payment
gateways.

# Requirements
* [Docker] (19.03.11 tested)
* [Docker Compose] (1.25.4 tested)

# Installation in Docker
1. Install git, Docker, Docker Compose:
```bash
sudo apt install git docker.io docker-compose
```
2. Clone the repository:
```bash
git clone https://github.com/fincubator/booker
cd booker
```
3. Start the services by running the command:
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
[Docker]: https://www.docker.com
[Docker Compose]: https://www.docker.com
