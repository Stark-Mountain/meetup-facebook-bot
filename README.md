# meetup-facebook-bot
FIXME: write the description

# Setup
1. Register [Facebook](https://developers.facebook.com/docs/messenger-platform/guides/setup) and [Heroku](https://dashboard.heroku.com) apps. 
2. Set environment variables: `VERIFY_TOKEN` is a Facebook verify token and `ACCESS_TOKEN` is a Facebook access token. Both were created during the first step.
3. Clone the repository.
4. [Set Heroku as a remote repository](https://stackoverflow.com/questions/5129598/how-to-link-a-folder-with-an-existing-heroku-app) and push the source to `heroku master`, effectively deploying the app.
5. Run `heroku run bash` and then `python3 initwelcome.py get_started -s 'get started payload'` to set "Get Started" button.
