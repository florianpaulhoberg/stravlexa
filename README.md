# Stravlexa - An Alexa Skill for Strava

This skill will provide you your latest sport activities on Strava for:
 - Running
 - Biking 
 - Swimming
It will also tell you your weight if provided/synced to Strava.

# Installation
- Copy Python script
- Modify your API key
- Mod your nginx to proxy to your stravlexa python script
- Setup Alexa Skill with provided intent schema

## Technical Aspects
This skill uses [Flask-Ask](https://flask-ask.readthedocs.io), a Python micro-framework that simplifies developing Alexa skills. Great work [John Wheeler](https://twitter.com/johnwheeler_)! With a little knowledge of Python and Flask it is very simple to extend.

### Nginx Configuration
> **Note:**
> - If you're not confident using Nginx see the [beginners guide](http://nginx.org/en/docs/beginners_guide.html)!
> - In order to be able to interact with Amazon Alexa, your endpoint either has to provide a certificate from a trusted certificate authority or you have to upload a self-signed certificate in X.509 format.

1) Add the following entry to your Nginx configuration (you may find it at /etc/nginx/sites-available/default):
```nginx
location /stravlexa {
rewrite ^/stravlexa/?(.*)$ /$1 break;
    proxy_pass http://localhost:5000;
    client_max_body_size 0;

    proxy_connect_timeout  36000s;
    proxy_read_timeout  36000s;
    proxy_send_timeout  36000s;
}
```
2) Restart Nginx.

3) Start the CALexa skill as well:
```sh
python /yourpathtocstravlexa/stravlexa.py
```
Your service will now be available via https://yourdomain/stravlexa/


## Configuration via Alexa Skills Kit

The configuration process is straigt forward, as known by other skills.
