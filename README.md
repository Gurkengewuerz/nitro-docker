# Nitro Docker installation
Nitro docker is a quick-to-setup docker environment for the [nitro client](https://github.com/billsonnn/nitro-react) with [Arcturus Community Emulator](https://git.krews.org/morningstar/Arcturus-Community). It can be run on Windows, Linux or OSX just with a few commands. It is inspired by [Holo5/nitro-docker](https://github.com/Holo5/nitro-docker).  
The default configuration can run on localhost.

**This Repository uses `ms4/dev` branch!**
**This Repository uses a [forked version](https://github.com/Gurkengewuerz/nitro) of Nitro with bug-fixes and more features!**

## Requirements
- Install docker desktop (and for windows, enable WSL support) [from here](https://www.docker.com/get-started/).
- Node.js 15.0 or higher (For the habbo-downloader)
- Clone this repository

## Build
1. Download the default assets

> The `&& \` is used to combine multiple commands into a single line in a Unix-like command shell. By using && \, the two commands are executed sequentially and only if the first command succeeds. If the first command fails, the second command will not be executed, saving you from potential errors.

```bash
git clone https://github.com/Gurkengewuerz/nitro-docker.git && \
cd nitro-docker/ && \
git clone https://git.krews.org/morningstar/arcturus-morningstar-default-swf-pack.git assets/swf/ && \
git clone https://github.com/krewsarchive/default-assets.git assets/assets/ && \
wget https://github.com/billsonnn/nitro-react/files/10334858/room.nitro.zip && \
unzip -o room.nitro.zip -d assets/assets/bundled/generic && \
docker compose up db -d
```
⚠ **The database port is exposed to `3010` by default** ⚠


2. Configure the `.env` to your needs

3. Download SQL updates: 
https://git.krews.org/morningstar/Arcturus-Community/-/archive/ms4/dev/Arcturus-Community-ms4-dev.zip?path=sqlupdates

4. Manually initialize database with HeidiSQL.
- Download `HeidiSQL` from: https://www.heidisql.com/download.php
- Open `HeidiSQL.exe` and connect to the nitro-docker-db container

```text
# **Default login credentials using HeidySQL:**
# Network type: MariaDB or MySQL (TCP/IP)
# Library: libmariadb.dll
# Hostname /IP: YOURSERVERIPHERE!!
# User: arcturus_user
# Password: arcturus_pw
# Port: 3310
# Databases: Separated by semicolon
```

- Select **arcturus**

- Go to **File** --> **Run SQL file...**  and open **arcturus_3.0.0-stable_base_database--compact.sql** Located at: nitro-docker/arcturus/arcturus_3.0.0-stable_base_database--compact.sql

- For the popup: Really auto-detect file encoding? click on **Yes**

- Go to **File** --> **Run SQL file...**  and open **3_0_0 to 3_5_0.sql** Located at: \Arcturus-Community-ms4-dev-sqlupdates\sqlupdates

- Go to **File** --> **Run SQL file...**  and open **3_5_0 to 4_0_0.sql**

- Go to **File** --> **Run SQL file...**  and open **4_0_0_pets_EN.sql**

- Go to **File** --> **Run SQL file...**  and open **4_0_0_permissions.sql**

- Go to **File** --> **Run SQL file...**  and open **perms_groups.sql** Located at: ./arcturus


5. Update emulator settings with HeidiSQL
> This will Disable console mode for Arcturus because we are using docker.

- Select `Query` then copy paste the follwing queries:

```sql
UPDATE emulator_settings SET `value`='http://127.0.0.1:8080/usercontent/camera/' WHERE  `key`='camera.url';

UPDATE emulator_settings SET `value`='/app/assets/usercontent/camera/' WHERE  `key`='imager.location.output.camera';

UPDATE emulator_settings SET `value`='/app/assets/usercontent/camera/thumbnail/' WHERE  `key`='imager.location.output.thumbnail';

UPDATE emulator_settings SET `value`='/app/assets/usercontent/badgeparts/' WHERE  `key`='imager.location.output.badges';

UPDATE emulator_settings SET `value`='/app/assets/swf/c_images/Badgeparts' WHERE  `key`='imager.location.badgeparts';

UPDATE emulator_settings SET `value`='0' WHERE `key`='console.mode';
```

- Press `F9` on your keyboard to run the queries

6. Start Asset Server, Build assets locally, Arcturus Community Emulator and Nitro

```bash
docker compose up assets -d && \
docker compose up assets-build --build && \
docker compose up imager --build -d && \
docker compose up arcturus --build -d && \
docker compose up backup -d
```

7. Update the: `nitro/renderer-config.json` and `nitro/ui-config.json` values to your setup. If the deployment is buggy or throws any errors check the json files for updates. then Build and Start Nitro

```bash
docker compose up nitro --build -d
```

> habbo-downloader requires **Node.js 15.0** or higher you can install the newest version with the following command:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash && \
nvm install node
```

> Next setup reverse proxies for your nginx or traefik server. You should disable proxy side caching.


## Update to latest production

8. Update a few assets since we want the most up to date assets as possible. You can remove habbo-downloader lines if needed or you can just download everything.

```text
# Replace `--domain de with` your own country code
# For example if you want Dutch then do `--domain nl`
# **Here is a list of supported country codes:**
# Portugese `--domain com.br`
# Turkish `--domain com.tr`
# English `--domain com`
# German `--domain de`
# Spanish `--domain es`
# Finnish `--domain fi`
# French `--domain fr`
# Italian `--domain it`
# Dutch `--domain nl`
```

```bash
apt install npm -y && \
npm i -g habbo-downloader && \
rm -rf assets/swf/gordon/PRODUCTION && \
habbo-downloader --output ./assets/swf --domain com --command badgeparts && \
habbo-downloader --output ./assets/swf --domain com --command badges && \
habbo-downloader --output ./assets/swf --domain com --command clothes && \
habbo-downloader --output ./assets/swf --domain com --command effects && \
habbo-downloader --output ./assets/swf --domain com --command furnitures && \
habbo-downloader --output ./assets/swf --domain com --command gamedata && \
habbo-downloader --output ./assets/swf --domain com --command gordon && \
habbo-downloader --output ./assets/swf --domain com --command hotelview && \
habbo-downloader --output ./assets/swf --domain com --command icons && \
habbo-downloader --output ./assets/swf --domain com --command mp3 && \
habbo-downloader --output ./assets/swf --domain com --command pets && \
habbo-downloader --output ./assets/swf --domain com --command promo && \
cp -n assets/swf/dcr/hof_furni/icons/* assets/swf/dcr/hof_furni && \
mv assets/swf/gordon/PRODUCTION* assets/swf/gordon/PRODUCTION && \
docker compose up assets-build --build
```


## Update Languages

```bash
habbo-downloader --output ./assets/translation --domain com --command gamedata && \
cd ./assets/translation && \
cp -rf gamedata/external*.txt ../swf/gamedata/ && \
cd ../.. && \
docker compose up assets-build --build && \
cd ./assets/translation && \
python FurnitureDataTranslator.py && \
python SQLGenerator.py 
```

* run SQL file

```bash
docker compose restart arcturus
```

## Create an archive/backup

```bash
7z a -mx=9 nitro-$(date -d "today" +"%Y%m%d_%H%M").7z ./
```
