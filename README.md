# ice\_launcher - Stream ffmpeg sources on demand for icecast2

## Introduction
This project starts an ffmpeg process on demand and sends its output to icecast2, when the icecast stream is accessed by a listener.
The aim of this project was to be able to convert a stream in HSL format ([HTTP Live Streaming](https://en.wikipedia.org/wiki/HTTP_Live_Streaming)) to an icecast stream.
This was to allow playing of an HSL stream to an older internet radio, when icecast support was dropped by a large UK media company.
Ideally this conversion of the stream should happen on demand, in order not to waste CPU power or bandwidth, particularly as we would like to convert several different streams when accessed.
Therefore this project listens to the icecast server and starts and stops the converting ffmpeg process as is needed.

At present the project only supports copying an input AAC stream to an icecast stream using ffmpeg.
Please note that for this purposes, the project is only for personal use.
If converting a copyrighted stream for general use, the owner should give permission.
Contributions to extend the functionality are welcomed.
This program is in an early state of development, so improvements are welcomed.

## Requirements

1. [Python 3.3+](https://python.org/)
2. [Icecast 2](https://icecast.org/)
3. [ffmpeg](https://ffmpeg.org/)

## How it works

ice\_launcher is a Python program which starts a simple HTTP server.
This server listens to authentication requests from an icecast2 server.
When icecast2 asks for authentication of a user to an unused mount, then an ffmpeg process is started to produce a source stream.
When the final listener finishes, then the corresponding ffmpeg process is closed.
ice\_launcher uses a configuration file defines the input streams and the connection details of the icecast2 server.

## Configuring icecast2

To make the icecast2 server send request to ice\_launcher, include something like the following in you `icecast.xml` configuration file:

    <mount type="default">
      <authentication type="url">
        <option name="listener_add" value="http://127.0.0.1:9854/" />
        <option name="listener_remove" value="http://127.0.0.1:9854/" />
      </authentication>
    </mount>

By default ice\_launcher listens on port 9854 of localhost.

## Configuring ice\_launcher

Please see the example `ice_launcher.conf` file included in this repository.
The defaults for options are shown commented out (with `#`).
There should be one `[main]` section defined with details about the icecast2 server.
For each stream there should be `[mount.mount_name]` defined, where `mount_name` is the mount of the stream on icecast2 (e.g. the stream is accessed like `http://localhost:8000/mount_name`).

### Main options

* `listen_address`: IP address to listen to (default 127.0.0.1). Using the default should ensure that connections can only originate from the local computer. It is not recommened to listen to an internet-wide port, as this program is not security-hardened.

* `listen_port`: Port to listen on (default 9854)

* `icecast_host`: IP address of icecast2 server (default 127.0.0.1)

* `icecast_port`: Port of icecast2 server (default 8000)

* `icecast_user`: icecast2 user for sources (default source)

* `icecast_password`: password for user (default password)

* `legacy_icecast`: set to True for icecast older than 2.4 (default False)

* `ffmpeg_wait`: how long in seconds to wait for ffmpeg to properly start (default 1.0)

* `ffmpeg_verbose`: show verbose output from ffmpeg (default False)

* `ffmpeg_agent`: if set, override the user agent of ffmpeg

* `log_level`: set output logging level (default info). Can be `critical`, `error`, `warning`, `info` or `debug`

### Mount-level options

* `input`: ffmpeg input (i.e. the input stream URL).

* `name`: user-visible source name passed to icecast2 (optional)

* `description`: user-visible source description passed to icecast2 (optional)

* `genre`: [genre](https://dir.xiph.org/genres) passed to icecast2 (optional)

* `public`: whether stream should be public (default False)

## Using icecast\_launcher

By default, the program will read configuration from the file `ice_launcher.conf`.
You can also pass an alternative configuration filename:

    ice_launcher.run --config=in.conf

## Notes on usage

* This code is not yet secure enough to use across the wider internet without great care!

* If using for non-personal use, please make sure that the copyright holder agrees with its use.

## Tested devices

* [Roberts 83i](https://www.robertsradiotechnical.co.uk/productpage.aspx?pid=STREAM%2083i)

## Future work

* Add user authentication

* Monitor ffmpeg status and restart if necessary
