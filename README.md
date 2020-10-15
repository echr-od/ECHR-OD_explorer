# ECHR OpenData Explorer

Install and run:

Starting the explorer requires ```docker```.

To build the environment image:
```
docker build -f Dockerfile -t echr_explorer .
```
As long as dependencies are not changed, there is no need to rebuild the image.

The container requires two mountpoints:
- the sources, mounted on `/tmp/echr_process/`
- the data folder `<build>` from ECHR process, mounted on `/tmp/echr_process/static/data/`

Once the image is built, the container is started with:
```
docker run -ti 
    --mount src=$(pwd),dst=/tmp/echr_explorer/,type=bind 
    --mount src=<build>,dst=/tmp/echr_explorer/static/build,type=bind echr_explorer
```