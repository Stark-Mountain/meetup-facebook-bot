# meetup-facebook-bot

[![Build Status][build-badge]][build]
[![Coverage Status][coverage-badge]][coverage]
[![Code Climate][code-climate-badge]][code-climate]
[![License: MIT][license-badge]][license]

[build-badge]: https://travis-ci.org/Stark-Mountain/meetup-facebook-bot.svg?branch=master
[build]: https://travis-ci.org/Stark-Mountain/meetup-facebook-bot
[coverage-badge]: https://coveralls.io/repos/github/Stark-Mountain/meetup-facebook-bot/badge.svg?branch=master
[coverage]: https://coveralls.io/github/Stark-Mountain/meetup-facebook-bot
[code-climate-badge]: https://codeclimate.com/github/Stark-Mountain/meetup-facebook-bot.png?branch=master
[code-climate]: https://codeclimate.com/github/Stark-Mountain/meetup-facebook-bot
[license-badge]: https://img.shields.io/badge/License-MIT-green.svg?branch=master
[license]: https://opensource.org/licenses/MIT
    
    
[<img src="https://github.com/fbsamples/messenger-bot-samples/blob/master/docs/assets/ViewMessenger.png" width="200">](https://m.me/cryptictor11398)

FIXME: write the description

# Setup
1. Register [Facebook](https://developers.facebook.com/docs/messenger-platform/guides/setup) and [Heroku](https://dashboard.heroku.com) apps. 
2. Set environment variables: `VERIFY_TOKEN` is a Facebook verify token and `ACCESS_TOKEN` is a Facebook access token. Both were created during the first step.
3. Set environment variable: `APP_ID`: To check your app_id: firstly login to https://developers.facebook.com/apps, then choose your app and copy APP_ID from top left corner of that page.
4. Set environment variable: `PAGE_ID`: Then navigate to your page, click on information, scroll to the bottom of the page and copy PAGE_ID.
5. Clone the repository.
6. [Set Heroku as a remote repository](https://stackoverflow.com/questions/5129598/how-to-link-a-folder-with-an-existing-heroku-app) and push the source to `heroku master`, effectively deploying the app.
7. Run `heroku run bash`. In here, setup the database with `python3 database_setup.py` and set "Get Started" button with ` python3 set_start_button.py`. (Do this only once)

# How to run tests
After all dependencies are installed (`pip3 install -r requirements.txt`), run the following command from the root folder of the project:

`$ python3 -m pytest tests --cov app --cov-report html`

View the generated html report with

`open htmlcov/index.html`
