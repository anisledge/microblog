# microblog

This is a blogging application using Python's [webapp2 module](https://webapp2.readthedocs.io/en/latest/), [jinja2](http://jinja.pocoo.org/docs/2.9/) templates, and the [Google App Engine](https://cloud.google.com/appengine/). Users can create an account, and login or out of their accounts. Users can also create blog posts, and edit or delete their posts, which are displayed on the users' home pages. The app was based on a project for Udacity's [Web Development](https://www.udacity.com/course/web-development--cs253) course.

**This project is currently in-progress.**

## Installation
### Google App Engine
This application uses the [Google App Engine](https://cloud.google.com/appengine/) and its corresponding [GQL Datastore](https://cloud.google.com/appengine/docs/python/datastore/gqlreference). In order to run the application without database access modification, you will need to download the Google Cloud SDK for Python. Please follow the [instructions on the Google Cloud website](https://cloud.google.com/appengine/docs/python/download).

### Setup
Clone or download the GitHub repository:

```
$ git clone https://github.com/anisledge/microblog
$ cd microblog
```

To use the security module, which provides cookie and password hashing, edit ```secrets_example.get()``` to return a unique ```key``` of your choosing. Then, rename secrets_example.py.
```
$ mv secrets_example.py secrets.py
```

### Usage
To run the application on a local server, use:
```
$ dev_appserver.py .
```
And open http://localhost:8080/ in a browser.

To deploy the application to Google App Engine, follow these [instructions](https://cloud.google.com/appengine/docs/python/getting-started/python-standard-env) from the Google Cloud website. You will need to create a free account.

## License
`microblog` is a public domain work, according to the [CCO 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) license.