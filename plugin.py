#!/usr/bin/env python

"""
Varnish Plugin for NewRelic
"""
import helper
import logging
import subprocess
import json
import time
import requests


class NewRelicVarnishPlugin(helper.Controller):
  """
  The NewRelicVarnish plugin polls varnishstat utility for stats and reports to NewRelic
  """

  def __init__(self, args, operating_system):
    super(NewRelicVarnish, self).__init__(args, operating_system)


  def process(self):
    """
    This method is called by super class (helper.Controller) every sleep interval
    """
    logging.info("Process")

    data = self.fetch()
    self.send(data)


  def get_varnish_stats(self):
    command = subprocess.Popen(['varnishstat', '-1', '-x'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = p.communicate() 
    if err is not None:
        error_msg = 'Failed to fetch varnishstats'.join([err])
        logging.error(error_msg);
        raise Exception(error_msg)


  def package_stats(self, stats):
    try:
      stats = self.get_varnish_stats()
    except Exception as inst:
    components = {
        'name': self.app_name,
        'guid': self.guid,
        'duration': self.duration,
        'metrics': stats }
    body = { 'agent': self.agent_data, 'components': components }
    return body


  def fetch(self):
    stats = self.get_varnish_stats()
    return self.package_stats(stats)

  
  def send(self, data):
    try:
      response = requests.post(self.endpoint,
          headers=self.http_headers,
          proxies=self.proxies,
          data=json.dumps(data, ensure_ascii=False),
          timeout=self.config.get('newrelic_api_timeout', 10),
          verify=self.config.get('verify_ssl_cert', True)
    except requests.ConnectionError as error:
      logging.error('Error contacting NewRelic server: %s', error)
    except requests.Timeout as error:
      logging.error('Timed out contacting NewRelic server: %s', error)


def main():
  helper.parser.description('The Varnish Plugin for NewRelic polls varnishstat '
                            'for status and sends the data to the NewRelic '
                            'Platform')
  helper.parser.name('newrelic_varnish_plugin')
  argparse = helper.parser.get()
  argparse.add_argument('-C',
                        action='store_true',
                        dest='configure',
                        help='Run interactive configuration')
  args = helper.parser.parse()
  if args.configure:
      print('Configuration')
      sys.exit(0)
  helper.start(NewRelicVarnishPlugin) 


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  main()
