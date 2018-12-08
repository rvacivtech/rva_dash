

## Initial Deploy Instructions
ssh to ubuntu machine
`sudo apt-get -y update`
`sudo apt-get install git supervisor nginx`
`git clone https://github.com/rvacivtech/rva_dash.git`
`cd rva_dash`
`curl https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh`
`sh miniconda.sh -b -p $HOME/miniconda`
`export PATH="$HOME/miniconda/bin:$PATH"`
`conda env create`
`source activate rva_dash`
create `config.ini` file based off of `config.ini.example`
`conda install gunicorn`
`echo "export FLASK_APP=rva_dash.py" >> ~/.profile`
`export FLASK_APP=rva_dash.py`
`nano /etc/supervisor/conf.d/rva_dash.conf`
Paste the following and save the file (`ctrl+x` to exit and save):
        ```
        [program:rva_dash]
        command=/home/miniconda3/rva_dash/envs/rva_dash/bin/gunicorn -b localhost:8000 -w 4 rva_dash:app
        directory=/home/ed_a_nunes_gmail_com/rva_dash
        user=ed_a_nunes_gmail_com
        autostart=true
        autorestart=true
        stopasgroup=true
        killasgroup=true
        ```
`sudo supervisorctl reload`
`mkdir certs`
`openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -keyout certs/key.pem -out certs/cert.pem`
`sudo rm /etc/nginx/sites-enabled/default`
`nano /etc/nginx/sites-enabled/rva_dash`
Paste the following and save the file (`ctrl+x` to exit and save):
        ```
        server {
            # listen on port 80 (http)
            listen 80;
            server_name _;
            location / {
                # redirect any requests to the same URL but on https
                return 301 https://$host$request_uri;
            }
        }
        server {
            # listen on port 443 (https)
            listen 443 ssl;
            server_name _;

            # location of the self-signed SSL certificate
            ssl_certificate /home/ed_a_nunes_gmail_com/rva_dash/certs/cert.pem;
            ssl_certificate_key /home/ed_a_nunes_gmail_com/rva_dash/certs/key.pem;

            # write access and error logs to /var/log
            access_log /var/log/rva_dash_access.log;
            error_log /var/log/rva_dash_error.log;

            location / {
                # forward application requests to the gunicorn server
                proxy_pass http://localhost:8000;
                proxy_redirect off;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }

            location /static {
                # handle static files directly, without forwarding to the application
                alias /home/ed_a_nunes_gmail_com/rva_dash/app/static;
                expires 30d;
            }
        }
        ```
`sudo service nginx reload`
Follow dirctions at https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx for SSL certificate.


##Code Upgrade Instructions
ssh to ubuntu machine
`cd rva_dash`
`sudo supervisorctl stop rva_dash`
`sudo supervisorctl start rva_dash`

#resources: 
* https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux
* https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx
* https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https