# Compiling OSM Proto
protoc is used to compile the latest proto files from
https://github.com/openstreetmap/OSM-binary/tree/master/src


## Install Protoc

Get the Latest Release from https://github.com/protocolbuffers/protobuf/releases

```bash
wget https://github.com/protocolbuffers/protobuf/releases/download/v21.6/protobuf-python-4.21.6.tar.gz

tar -xvzf protobuf-python-4.21.6.tar.gz

cd protobuf-4.21.6/
./configure
make
make check
sudo make install
sudo ldconfig

protoc --version
```

## Generate fileformat_pb2.py and osmformat_pb2.py
from root dir (i.e earth_osm)
```bash
protoc -I=./ --python_out=./ ./earth_osm/osmpbf/fileformat.proto ./earth_osm/osmpbf/osmformat.proto
```
