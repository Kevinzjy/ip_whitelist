import ipaddress
import cherrypy
from cherrypy.lib import auth_digest
from cherrypy.process.plugins import Daemonizer
from subprocess import getstatusoutput

WHITELIST_FILE='./iptables_rules.txt'

html_header = '''
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Login</title>
    <link rel="icon" href="https://cdnjs.cloudflare.com/ajax/libs/octicons/8.5.0/svg/lock.svg" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic" />
    <link rel="stylesheet" href="https://pagecdn.io/lib/milligram/v1.3.0/milligram.min.css" />
    <link rel="stylesheet" href="https://milligram.io/styles/main.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/webicons/2.0.0/webicons.min.css">
  </head>
  <body>
    <main class="wrapper">
      <nav class="navigation">
        <section class="container">
          <a class="navigation-title" href="/">
            <embed src="https://cdnjs.cloudflare.com/ajax/libs/octicons/8.5.0/svg/lock.svg" viewBox="0 0 463 669"/>
            &nbsp;
            <h1 class="title">IP Whitelist</h1>
          </a>
        </section>
      </nav>
      <section class="container" id="Login">
'''

html_footer = '''
      </section>
    </main>
    <script src="https://milligram.io/scripts/main.js"></script>
  </body>
</html>
'''


class Subscribe(object):

    @cherrypy.expose
    def index(self, **kwargs):
        ip = cherrypy.request.headers['Remote-Addr']
        if ip.startswith('::ffff:'):
            ip = ip[7:]

        html_body = '''
                <form method="post" action="login">
                  <fieldset>
                    <label for="ip">IP address</label>
                    <input type="text" placeholder="{0}" name="ip" value="{0}">
                    <input class="button-primary" type="submit" value="Subscribe">
                  </fieldset>
                </form>
        '''.format(ip)

        return html_header + html_body + html_footer

    @cherrypy.expose
    def login(self, **kwargs):
        try:
            tmp_ip = kwargs['ip'] if ('ip' in kwargs and kwargs['ip']) else cherrypy.request.headers['Remote-Addr']:
            if tmp_ip.startswith('::ffff:'):
                tmp_ip = tmp_ip[7:]
            ip = ipaddress.ip_address(tmp_ip)

            whitelist = load_whitelist()
            if str(ip) in whitelist:
                ret = 'IPv{} address: {} already in whitelist'.format(ip.version, ip)
            else:
                status = add_ip(str(ip))
                if status == 0:
                    ret = 'Successfully added IPv{} address: {} to whitelist'.format(ip.version, ip)
                else:
                    ret = 'IPv{} address: {} already in iptables rules'.format(ip.version, ip)
        except ValueError:
            ret = 'Error: {} is not a valid ip address'.format(kwargs['ip'])

        html_body = '''<p> <b> {} </b> </p>
        <a class="button" href="/">Return</a>
        '''.format(ret)
        return html_header + html_body + html_footer


def load_whitelist():
    ips = []
    try:
        with open(WHITELIST_FILE, 'r') as f:
            for line in f:
                ip = line.rstrip()
                if ip:
                    ips.append(ip)
    except FileNotFoundError:
        f = open(WHITELIST_FILE, 'w')
        f.close()
    return ips


def add_ip(ip):
    with open(WHITELIST_FILE, 'a') as f:
        f.write(ip + '\n')
    status, res = getstatusoutput('./update_ip.sh {}'.format(str(ip)))
    return status


def main():
    USERS = {'USER': 'PASSWORD'}
    cherrypy.config.update({
        'server.socket_host': '::',
        'server.socket_port': 8080,
    })
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'localhost',
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(USERS),
            'tools.auth_digest.key': '3f80c187d4fbbb054b4f24ab1f3cb231',
            'tools.auth_digest.accept_charset': 'UTF-8',
        },
    }
    webapp = Subscribe()

    cherrypy.quickstart(webapp, '/', conf)


d = Daemonizer(cherrypy.engine)
d.subscribe()
main()
