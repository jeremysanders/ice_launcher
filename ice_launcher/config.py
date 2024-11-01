# icelaunch: Read configuration
#
# Copyright Jeremy Sanders (2023)
# Released under the MIT Licence

import configparser
import os.path

class Option:
    '''Define option in configuration file.

    name: name of option
    default: default value if not present
    dtype: data type: 'str', 'int', 'bool', 'float'
    '''

    def __init__(self, name, default=None, dtype='str'):
        self.name = name
        self.default = default
        self.dtype = dtype

    def get(self, section):
        '''Get option value from conf file section.'''
        if self.name not in section:
            return self.default
        if self.dtype == 'bool':
            return section.getboolean(self.name)
        elif self.dtype == 'int':
            return section.getint(self.name)
        elif self.dtype == 'float':
            return section.getfloat(self.name)
        elif self.dtype == 'str':
            return section[self.name]
        else:
            raise RuntimeError('Unknown dtype')

# options in [main] section
main_opts = [
    Option('listen_address', default='127.0.0.1'),
    Option('listen_port', default=9854, dtype='int'),

    Option('icecast_host', default='127.0.0.1'),
    Option('icecast_port', default=8000, dtype='int'),
    Option('icecast_user', default='source'),
    Option('icecast_password', default='password'),
    Option('icecast_forbid_status', default=False, dtype='bool'),
    Option('legacy_icecast', default=False, dtype='bool'),

    Option('allow_users'),

    Option('ffmpeg_wait', default=1.0, dtype='float'),
    Option('ffmpeg_verbose', default=False, dtype='bool'),
    Option('ffmpeg_agent'),

    Option('log_level', default='info'),
]

allowed_modes = set(['copy_aac', 'copy_mp3'])

# options in [mount.X] sections
mount_opts = [
    Option('mode', default='copy_aac'),
    Option('input'),
    Option('name'),
    Option('description'),
    Option('genre'),
    Option('public', default=False),
]

class Config:
    '''Define set of configuration settings read from conf file.'''

    def __init__(self, filename):
        conffile = configparser.ConfigParser()
        if not os.path.exists(filename):
            raise RuntimeError(
                'Configuration file "%s" does not exist' % filename)
        conffile.read(filename)

        # read main section
        self.main = {}
        mainsect = conffile['main']
        for opt in main_opts:
            self.main[opt.name] = opt.get(mainsect)

        # convert users
        self.allow_users = {}
        if self.main['allow_users']:
            for user_passwd in self.main['allow_users'].split():
                s = user_passwd.split(':')
                if len(s) != 2:
                    raise RuntimeError(
                        'User password combination invalid: "%s"' % user_passwd)
                self.allow_users[s[0]] = s[1]

        # read sections for each mount (called mount.X)
        self.mounts = {}
        for sect in conffile.sections():
            if sect[:6] == 'mount.':
                mount = sect[6:]
                self.mounts[mount] = {}
                for opt in mount_opts:
                    self.mounts[mount][opt.name] = opt.get(conffile[sect])

                # checks for options
                mode = self.mounts[mount]['mode']
                if mode not in allowed_modes:
                    raise RuntimeError('Mode "%s" is unknown' % mode)
                if not self.mounts[mount]['input']:
                    raise RuntimeError('No input given for mount "%s"' % mount)
