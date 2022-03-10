# ap-parse

Parser for iw and iwinfo on OpenWrt devices. Currently supports only device list and connected
stations data. Output from iw and iwinfo on other platforms might work, but it's not tested.


## Table of contents

- [Installation](#installation)
- [Usage](#usage)
  - [CLI](#cli)
  - [API](#api)
- [License](#license)


## Installation

```sh
python -m pip install -U ap-parse
```


## Usage

Log in to the device via SSH and run the the command of choice. Feed the output to ap-parse either
programmatically or via the CLI.

- List devices with iw:
  ```sh
  iw dev
  ```

- List stations with iw:
  ```sh
  iw dev <device name> station dump
  ```

- List devices with iwinfo:
  ```sh
  iwinfo
  ```

- List stations with iwinfo:
  ```sh
  iwinfo <device name> assoclist
  ```

### CLI

Pipe the command output to ap-parse. Example for iwinfo device list:
```
ssh <user@host> iwinfo | python -m apparse iwinfo device
```

| Argument | Type | Values              | Description                              |
|----------|------|---------------------|------------------------------------------|
| backend  | str  | `iw`, `iwinfo`      | Utility used to generate the output data |
| type     | str  | `device`, `station` | Type of the output data                  |

### API

Save the command output to a file and pass it as a string to the appropriate parser.
Example for iwinfo device list:
```sh
ssh <user@host> iwinfo > output.txt
```

```python
import apparse

with open('output.txt', 'r', encoding='utf-8') as f:
    raw_data = f.read()

parsed_data = apparse.parse_iwinfo_station(raw_data)
print(parsed_data)
```

In case you wish to add or remove fields or modify regexes, subclass one of the parser classes under
its respective module `apparse.*_parser`.


## License

MIT license. See [LICENSE][license] for more information.


[license]: https://github.com/alexitx/ap-parse/blob/master/LICENSE
