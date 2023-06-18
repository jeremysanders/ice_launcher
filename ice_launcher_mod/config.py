import configparser

class Option:
    '''Define option in ConfigFile.

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

    Option('icecast_host', default='localhost'),
    Option('icecast_port', default=8000, dtype='int'),
    Option('icecast_user', default='source'),
    Option('icecast_password', default='password'),
    Option('legacy_icecast', default=True, dtype='bool'),

    Option('ffmpeg_wait', default=1.0, dtype='float'),
    Option('ffmpeg_verbose', default=False, dtype='bool'),
    Option('ffmpeg_agent'),
]

allowed_modes = set(['copy_aac'])

# options in [mount.X] sections
mount_opts = [
    Option('mode', default='copy_aac'),
    Option('url'),
    Option('name'),
    Option('description'),
    Option('genre'),
]

class Config:
    '''Define set of configuration settings read from conf file.'''

    def __init__(self, filename):
        conffile = configparser.ConfigParser()
        conffile.read(filename)

        # read main section
        self.main = {}
        mainsect = conffile['main']
        for opt in main_opts:
            self.main[opt.name] = opt.get(mainsect)

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
                    raise RuntimeError('Mode %s is unknown' % mode)
                if not self.mounts[mount]['url']:
                    raise RuntimeError('No URL given for mount %s' % mount)
