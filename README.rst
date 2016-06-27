Open VEDA / VEDA Node
=====================

A general-purpose bundle to transcode video for instances of open-edx
---------------------------------------------------------------------

[v0.1] / 2016.06
~~~~~~~~~~~~~~~~

--------------

Installation
------------

::
    **STILL IN ALPHA**
    ~~pip install openveda~~


**you will need ffmpeg**  most likely with libx264 & libmp3lame  
| compilation instructions here https://trac.ffmpeg.org/wiki/CompilationGuide

Usage
-----

**Sample Usage** instantiate class:

::

    OV = openVEDA(
        mezz_video='/path/to/video_i_want_to_process.mp4'
        settings_file='/path/to/edited_settings_file.py', 
        )

in **settings.py**:

::

    VAL_ATTACH = True
    VAL_TOKEN_URL='https://this_is_where_i_get_a/token'
    VAL_API_URL='https://this_is_where_i_send/data_to_val' 
    VAL_CLIENT_ID='my_API_client_id'
    VAL_CLIENT_SECRET='my_API_secret_key'
    VAL_USERNAME='edx_username'
    VAL_USERPASS='edx_userpass'

**-or-**

instantiate class:

::

    OV = openVEDA(
        mezz_video='/path/to/video_i_want_to_process.mp4'
        VAL_ATTACH=True,
        VAL_TOKEN_URL='https://this_is_where_i_get_a/token',
        VAL_API_URL='https://this_is_where_i_send/data_to_val',
        VAL_CLIENT_ID='my_API_client_id',
        VAL_CLIENT_SECRET='my_API_secret_key',
        VAL_USERNAME='edx_username',
        VAL_USERPASS='edx_userpass',
        )

See below for API usage

Test your config
----------------

(will attempt to contact storage endpoints and APIs attached)

::

    OV.test()

Encode, Deliver, and Report video
---------------------------------

::

    OV.activate()

Does openveda think it completed?
---------------------------------

::

    complete = OV.complete()

--------------

Methods:
--------

One can either edit and move the settings.py file, (provided in root),
and point to it via full filepath argument:

::

    OV = openVEDA(
        settings_file='/path/to/edited_settings_file', 
        mezz_video='/path/to/video_i_want_to_process.mp4'
    )

Or each of the settings can be provided as an argument, provided with
some basic documentation below

Basic Settings
~~~~~~~~~~~~~~

The only mandatory argument to pass to openVEDA:

``mezz_video`` (string) either filepath to a local video or an AWS S3
keyname (e.g. Name of object in bucket)

::

    openVEDA(
        mezz_video='my/video.mp4'
        )

or

::

    openVEDA(
        mezz_video='s3_object_name'
        )

``settings_file`` (string) - filepath to (optional, but recommended)
settings.py file

``encode_library`` (string) - filepath to (optional) json of encoding
profiles, defaults to ``default_encode_profiles.json``

``workdir`` (string, dirname) - filepath to encode directory.
Defaults to current working directory.

--------------

edx-Studio interface
~~~~~~~~~~~~~~~~~~~~

| ``EDX_STUDIO_UPLOAD`` (bool)
| Is the edx-studio video upload page active? This will copy the file
  **to** the hotstore directory/bucket and **from** the ingest
  directory/bucket.
|
| ``MEZZ_INGEST_LOCATION`` (string)
| A folder or bucket to look for new files in. Files will be copied to
  hotstore and then deleted from ingest location.
|
| ``S3_ASSET_STORE`` (bool)
| Is hotstore (a short/long term place for videos openveda is done with)
  an S3 bucket?
|
| ``MEZZ_HOTSTORE_LOCATION`` (string)
| This is where openveda will copy files once they're ingested, if this
  is desired. Either a bucket name (S3), full filepath (local) or URL.
|
| ``S3_DELIVER`` (bool)
| Deliver completed encodes to S3 for serving?
|
| ``DELIVERY_ENDPOINT`` (string) Location to deliver completed encodes for
serving. Either a bucket name (S3), full filepath (local) or URL.
|
| ``SSL_ENDPOINT`` (string) Is delivery endpoint an SSL enabled (https)
endpoint? Ignored for Local or S3 endpoints

AWS S3 Credentials
~~~~~~~~~~~~~~~~~~

| ``S3_ACCESS_KEY_ID``
| ``S3_SECRET_ACCESS_KEY``

| Note: if the endpoint and hotstore/ingest account credentials are
  different, the following args may be passed as either S3 access keys
  or FTP credentials:
| ``DELIVERY_ID`` 
| ``DELIVERY_PASS``

Video Abstraction Layer API (edx-val)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check documentation for edx-val for setup and interface, this is by no
means a shortcut for that

| ``VAL_ATTACH`` (bool) - is this connected to an instance of edx-val?
| ``VAL_TOKEN_URL`` (string) - full url to generate auth token for VAL
| ``VAL_API_URL`` (string) - full url to VAL API endpoint

Credentials
^^^^^^^^^^^

| ``VAL_CLIENT_ID`` (string) - API Client ID
| ``VAL_CLIENT_SECRET`` (string) - API Client Secret
| ``VAL_USERNAME`` (string) - edx username w/ VAL edit/delete
  credentials
| ``VAL_USERPASS`` (string) - edx userpass

--------------

TODO:
-----
| [ ] Nose Tests
| [ ] Requirements 
| [ ] PEP8/Pylint
| [ ] Licensing

**@yro / 2016**