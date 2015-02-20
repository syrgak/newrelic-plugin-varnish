#!/usr/bin/env python

"""
Varnish Plugin for NewRelic
"""
from xml.etree import ElementTree
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


  def setup(self):
    self.http_headers['X-License-Key'] = self.license_key


  @property
  def http_headers(self):
    return {
      'Accept': 'application/json',
      'Content-Type': 'application/json'}


  @property
  def license_key(self):
    return self.config.application.license_key


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
    return out


  def parse(self, output):
      result = []
      try:
        stats = ElementTree.XML(output)
      expect Exception:
        raise
      for stat in stats.iter(tag='stat'):
          metrics = []
          for prop in stat:
              metrics.append((prop.tag, prop.text))
          result.append(dict(metrics))
      return result


  def package_stats(self, stats):
    components = {
        'name': self.app_name,
        'guid': self.guid,
        'duration': self.duration,
        'metrics': stats }
    body = { 'agent': self.agent_data, 'components': components }
    return body


  def fetch(self):
    try:
      xml = self.get_varnish_stats()
      stats = self.parse(xml)
    except Exception as inst:
      raise
    return self.package_stats(stats)

  
  def send(self, package):
    try:
      response = requests.post(self.endpoint,
          headers=self.http_headers,
          proxies=self.proxies,
          data=json.dumps(package, ensure_ascii=False),
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
