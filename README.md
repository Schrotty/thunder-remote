# Thunder-Remote

## Install

Install through pypi:

    pip install thunder-remote
    
After the setup is complete run the following command to patch the inputs library for non-blocking controller input.
Otherwise the library blocks until there is an input from the controller.

    python -m thunder_remote --patch

Or clone this repo:

    git clone https://github.com/Schrotty/thunder-remote
    cd thunder-remote
    python setup.py install

## Usage

For examples see the _examples/_ directory.

## License
Thunder-Remote is licensed under the MIT-License.

The 3rd-party module licenses can be found in _LICENSE-3RD-PARTY.md_