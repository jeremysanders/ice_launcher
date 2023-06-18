import subprocess
import time
import logging

def start_source(mount, config):
    """Start source for mount given."""

    # config options for mount
    mount_config = config.mounts[mount]

    cmd = [
        'ffmpeg',
        '-re',   # realtime
        '-i', mount_config['url'], # input url
        '-vn',   # no video
    ]

    if mount_config['mode'] == 'copy_aac':
        cmd += get_options_mode_copy_aac(mount, config)
    else:
        raise RuntimeError('Invalid mode')

    # optional icecast arguments
    for confname, ffmpegopt in (
            ('name', '-ice_name'),
            ('description', '-ice_description'),
            ('genre', '-ice_genre'),
            ):
        val = mount_config[confname]
        if val:
            cmd += [ffmpegopt, val]

    # disable ffmpeg output if not verbose
    if not config.main['ffmpeg_verbose']:
        cmd += ['-loglevel', 'error', '-hide_banner']

    if config.main['legacy_icecast']:
        cmd += ['-legacy_icecast', '1']
    if config.main['ffmpeg_agent']:
        cmd += ['-user_agent', config.main['ffmpeg_agent']]

    # output connection
    cmd.append('icecast://%s:%s@%s:%d/%s' % (
        config.main['icecast_user'],
        config.main['icecast_password'],
        config.main['icecast_host'],
        config.main['icecast_port'],
        mount,
    ))
    logging.info(" starting ffmpeg command for mount %s (%s)" % (
        mount, str(cmd)))

    # start ffmpeg process
    popen = subprocess.Popen(cmd)

    # wait until ffmpeg is hopefully running ok
    # there should be a better way to do this, but ffmpeg output needs to be parsed
    time.sleep(config.main['ffmpeg_wait'])

    return popen

def get_options_mode_copy_aac(mount, config):
    """Specific options for copy_aac mode."""
    return [
        '-acodec', 'copy',
        '-content_type', 'audio/aac',
        '-f', 'adts',
    ]
