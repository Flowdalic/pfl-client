# standard library
import sys
import json
from datetime import datetime

# external library
# portage api: sys-apps/portage
import portage
# dev-python/termcolor
from termcolor import colored
# http: dev-python/requests
import requests

VERSION='3.5'
BASEURL='https://www.portagefilelist.de/query.php?file=%s'

# the main method to run this.
# options are
# options = {
#      'file': '',
#      'stdout': False
#  }
# Use options['stdout'] = True if you wan to run this as a script which prints the output as it happens.
# With False the output is collected and returned, so no immediate display what is going on.
def run(options):
    start = Efile(options)
    return start.run()

class Efile(object):
    _options = None
    _out = ''

    def __init__(self, options):
        self._options = options

    def log(self, output=''):
        if 'stdout' in self._options and self._options['stdout'] :
            print(output)
        else:
            self._out += output + '\n'

    def run(self):
        ret, jsonData = self.doRequest()
        if(jsonData):
            cps = {}
            for file in jsonData:
                category = file['category']
                package = file['package']
                version = file['version']
                filepath = file['path']
                repo = file['repository']

                if not category in cps:
                    cps[category] = {}

                if not package in cps[category]:
                    cps[category][package] = {
                            'versions': [version],
                            'files': [filepath]
                            }
                else:
                    cps[category][package]['versions'].append(version)
                    cps[category][package]['files'].append(filepath)

            eroot = portage.settings['EROOT']
            vardbapi = portage.db[eroot]['vartree'].dbapi
            portdbapi = portage.db[eroot]['porttree'].dbapi
            for category, packages in cps.items():
                for package, vf in packages.items():
                    installed_cpvs = sorted(set(vardbapi.cp_list('%s/%s' % (category, package))))
                    available_cpvs = sorted(set(portdbapi.cp_list('%s/%s' % (category, package))))

                    installed = False
                    if len(installed_cpvs) > 0:
                        installed = True

                    # *  category/package
                    #[I] category/package
                    _toPrint = ''
                    if installed:
                        _toPrint = colored('[I] ', 'green')
                    else:
                        _toPrint = colored(' * ', 'green')
                    self.log('%s %s/%s' % (_toPrint, category, package))

                    #        Seen Versions:          X.Y A.B
                    versions = sorted(set(vf['versions']))
                    self.log(colored('\tSeen Versions:'.ljust(22), 'green') + '%s' % ' '.join(versions))

                    #        Portage Versions:       X.Y A.B
                    _toPrint = colored('\tPortage Versions:'.ljust(22), 'green')
                    for available_cpv in available_cpvs:
                        _toPrint += portage.versions.cpv_getversion(available_cpv)
                    self.log(_toPrint)

                    #        Repository:             Name
                    self.log(colored('\tRepository:'.ljust(22), 'green') + repo)

                    # old:
                    #        Last Installed Ver:     X.Y(Thu Apr 2 01:01:19 2020)
                    # new:
                    #        Installed Versions:     X.Y(Thu Apr 2 01:01:19 2020)
                    if installed:
                        _toPrint = colored('\tInstalled Versions:'.ljust(22), 'green')
                        for installed_cpv in installed_cpvs:
                            build_time, = vardbapi.aux_get(installed_cpv, ['BUILD_TIME'])
                            try:
                                build_time = build_time = int(build_time.strip())
                            except ValueError:
                                build_time = 0
                            _toPrint += colored(portage.versions.cpv_getversion(installed_cpv), 'white', 'on_blue')
                            _toPrint += colored(datetime.fromtimestamp(build_time).strftime('(%c) '), 'magenta')
                        self.log(_toPrint)

                    if len(available_cpvs) > 0:
                        description, homepage = portdbapi.aux_get(available_cpvs[-1], ['DESCRIPTION', 'HOMEPAGE'])

                        #        Homepage:               http://example.org
                        self.log(colored('\tHomepage:'.ljust(22), 'green') + '%s' % homepage)

                        #        Description:            package description
                        self.log(colored('\tDescription:'.ljust(22), 'green') + '%s' % description)

                    #        Matched Files:          /the/found/file; /another/found/file;
                    files = sorted(set(vf['files']))
                    self.log(colored('\tMatched Files:'.ljust(22), 'green') + '%s' % '; '.join(files))
                    self.log('')

            return 0, self._out
        else:
            self.log('Something went wrong with the request result.')
            self.log(jsonData)

        return 1, self._out

    def doRequest(self):
        try:
            r = requests.get(BASEURL % self._options['file'])
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.log("An HTTP error occured")
            raise SystemExit(e)
        except requests.exceptions.ConnectionError as e:
            self.log("An connection error occured")
            raise SystemExit(e)
        except requests.exceptions.Timeout as e:
            self.log("Timeout")
            raise SystemExit(e)
        except requests.exceptions.RequestException as e:
            self.log("Something went totally wrong with the request")
            raise SystemExit(e)

        resultJson = json.loads(r.text)

        if 'error' in resultJson:
            self.log(resultJson['error']['code'])
            self.log(resultJson['error']['message'])
            return 1, ''
        elif 'result' in resultJson:
            if len(resultJson['result']) > 0:
                return 0, resultJson['result']
            else:
                self.log('Empty result return. This should not happend.')
                return 1, ''
        else:
            self.log('Something went wrong with the request result.')
            self.log(resultJson)
            return 1, ''

        return 1, ''
