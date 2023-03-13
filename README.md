# Nitro Docker installation
Nitro docker is a quick-to-setup docker environment for the [nitro client](https://github.com/billsonnn/nitro-react) with [Arcturus Community Emulator](https://git.krews.org/morningstar/Arcturus-Community). It can be run on Windows, Linux or OSX just with a few commands. It is inspired by [Holo5/nitro-docker](https://github.com/Holo5/nitro-docker).  
The default configuration can run on localhost.

## Requirements
- Install docker desktop (and for windows, enable WSL support) [from here](https://www.docker.com/get-started/).
- Clone this repository

## Build
1. Clone default SWF pack
```bash
# download SWFs
git clone https://git.krews.org/morningstar/arcturus-morningstar-default-swf-pack.git assets/swf/
```

2. Download default assets
```bash
# download assets
git clone https://github.com/krewsarchive/default-assets.git assets/assets/
```

3. Take a look at `.env` file an configure to your needs

4. Start database  
⚠ **The database port is exposed to `3010` by default** ⚠
```bash
# start database
docker compose up db -d
```

5. Manually initialize database  
Setup using `arcturus/arcturus_3.0.0-stable_base_database--compact.sql` and the correct SQL Updates from [Arcturus sqlupdates](https://git.krews.org/morningstar/Arcturus-Community/-/tree/master/sqlupdates).
The first database come from mysql/dumps, it's the base Arcturus database for 3.0.X with just a default SSO ticket (123) useable via http://127.0.0.1:1080?sso=123


6. Update emulator settings  
Disable console mode for Arcturus because we are using docker. To update the arcturus database preferably use rcon. To update a `user_` table disconnect the user. To update the `emulator_settings` table stop the server.
```sql
-- update value path to the assets server
UPDATE emulator_settings SET `value`='http://127.0.0.1:8080/usercontent/camera/' WHERE  `key`='camera.url';
-- do not touch the following values - they use docker volume paths
UPDATE emulator_settings SET `value`='/app/assets/usercontent/camera/' WHERE  `key`='imager.location.output.camera';
UPDATE emulator_settings SET `value`='0' WHERE `key`='console.mode';
```

7. Start Asset Server
```bash
# start asset server
docker compose up assets -d
```

8. Build assets locally
```bash
# build the nitro assets
docker compose up assets-build
```

9. Build and Start Arcturus Community Emulator
```bash
# start Arcturus emulator
docker compose up arcturus
```

10. Update `nitro/renderer-config.json` and `nitro/ui-config.json` values to your setup. If the deployment is buggy or throws any errors check the json files for updates.

11. Build and Start Nitro
```bash
# start nitro server
docker compose up nitro
```

Next setup reverse proxies for your nginx or traefik server.

## Update to latest production
Update a few assets since we want the most up to date assets as possible.

```bash
npm i -g habbo-downloader
rm -rf assets/swf/gordon/PRODUCTION
habbo-downloader --output ./assets/swf --domain com --command SEE_LIST_BELOW
cp -n assets/swf/dcr/hof_furni/icons/* assets/swf/dcr/hof_furni
mv assets/swf/gordon/PRODUCTION* assets/swf/gordon/PRODUCTION
```

```
badgeparts
badges
clothes
effects
furnitures
gamedata
gordon
hotelview
icons
mp3
pets
promo
```

After all update nitro files
```bash
docker compose up assets-build
```


## Update Languages

```bash
habbo-downloader --output ./assets/translation --domain de --command gamedata
cd ./assets/translation
cp -rf gamedata/external*.txt ../swf/gamedata/
cd ../..
docker compose up assets-build
cd ./assets/translation
python FurnitureDataTranslator.py
python SQLGenerator.py
# run SQL file
# restart emulator
```

## Create an archive/backup

```bash
7z a -mx=9 nitro-$(date -d "today" +"%Y%m%d_%H%M").7z ./
```
