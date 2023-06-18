# icelaunch: Launch sources
#
# Copyright Jeremy Sanders (2023)
# Released under the MIT Licence

import subprocess
import time
import logging

class IceLaunchError(RuntimeError):
    """Exception for problems launching the process."""
    pass

def start_source(mount, conf):
    """Start source for mount given."""

    # conf options for mount
    mount_conf = conf.mounts[mount]

    cmd = [
        'ffmpeg',
        '-re',   # realtime
        '-i', mount_conf['url'], # input url
        '-vn',   # no video
    ]

    if mount_conf['mode'] == 'copy_aac':
        cmd += get_options_mode_copy_aac(mount, conf)
    else:
        raise RuntimeError('Invalid mode')

    # optional icecast arguments
    for confname, ffmpegopt in (
            ('name', '-ice_name'),
            ('description', '-ice_description'),
            ('genre', '-ice_genre'),
            ):
        val = mount_conf[confname]
        if val:
            cmd += [ffmpegopt, val]

    # is this a public stream? (0=False)
    cmd += ['-ice_public', str(int(mount_conf['public']))]

    # disable ffmpeg output if not verbose
    if not conf.main['ffmpeg_verbose']:
        cmd += ['-loglevel', 'error', '-hide_banner']

    if conf.main['legacy_icecast']:
        cmd += ['-legacy_icecast', '1']
    if conf.main['ffmpeg_agent']:
        cmd += ['-user_agent', conf.main['ffmpeg_agent']]

    # output connection
    cmd.append('icecast://%s:%s@%s:%d/%s' % (
        conf.main['icecast_user'],
        conf.main['icecast_password'],
        conf.main['icecast_host'],
        conf.main['icecast_port'],
        mount,
    ))
    logging.info(" starting ffmpeg command for mount %s (%s)" % (
        mount, str(cmd)))

    # start ffmpeg process
    try:
        popen = subprocess.Popen(cmd)
    except Exception:
        logging.error('ffmpeg process for mount "%s" did not start' % mount)
        raise IceLaunchError('ffmpeg process failed to start')

    # wait until ffmpeg is hopefully running ok
    # there should be a better way to do this, but ffmpeg output needs to be parsed
    time.sleep(conf.main['ffmpeg_wait'])

    if popen.poll() is not None:
        logging.error(
            'ffmpeg process for mount "%s" died after starting' % mount)
        raise IceLaunchError('ffmpeg process failed to start')

    return popen

def get_options_mode_copy_aac(mount, conf):
    """Specific options for copy_aac mode."""
    return [
        '-acodec', 'copy',
        '-content_type', 'audio/aac',
        '-f', 'adts',
    ]
