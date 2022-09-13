# Fasteners

Python standard library provides an Exclusive Lock for threads and Exclusive Lock for processes
spawned by `multiprocessing` module. `fasteners` provides additional three synchronization primitives:

* Exclusive Lock for independent processes
* Readers Writer Lock for independent processes
* Readers Writer Lock for threads

## Installation

```
pip install fasteners
```

## Usage

See [User Guide](guide/index.md) for usage tips and examples and [Reference](api/inter_process.md) for detailed API.

## Similar libraries

[`portarlocker`](https://github.com/WoLpH/portalocker): readers writer lock and semaphore for 
independent processes, exclusive lock based on redis. 

[`py-filelock`](https://github.com/tox-dev/py-filelock): exclusive lock for independent processes.

[`pyReaderWriterLock`](https://github.com/elarivie/pyReaderWriterLock): inter-thread readers writer 
locks, optionally downgradable, with various priorities (reader, writer, fair).