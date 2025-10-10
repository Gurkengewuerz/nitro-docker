# Nitro Docker installation
Nitro docker is a quick-to-setup docker environment for the [nitro client](https://github.com/billsonnn/nitro-react) with [Arcturus Community Emulator](https://git.krews.org/morningstar/Arcturus-Community). It can be run on Windows, Linux or OSX just with a few commands. It is inspired by [Holo5/nitro-docker](https://github.com/Holo5/nitro-docker).  
The default configuration can run on localhost.

**This Repository uses `ms4/dev` branch!**
**This Repository uses a [forked version](https://github.com/Gurkengewuerz/nitro) of Nitro with bug-fixes and more features!**

## Requirements
- Install docker desktop (and for windows, enable WSL support) [from here](https://www.docker.com/get-started/).
- Node.js LTS or higher (For the habbo-downloader)
- Clone this repository

## Notes
This setup installs a complete local setup. Connecting externally requires editing the configurations. Serach for the following ports and edit them. Down below is a recommended domain setup when using reverse proxies like traefik.

| Server                | Local Setup           | Recommended Domain Setup |
|-----------------------|-----------------------|--------------------------|
| MorningStar WebSocket | ws://127.0.0.1:2096   | game.example.com         |
| Assets Server         | http://127.0.0.1:8080 | assets.example.com       |
| CMS                   | http://127.0.0.1:8081 | example.com              |
| Nitro Client          | http://127.0.0.1:3080 | game.example.com         |

```sql
UPDATE emulator_settings SET `value`='*.example.com' WHERE  `key`='websockets.whitelist';
```

## Build
0. copy necessary files to work locally
The following command searches for all files starting with `example-`, copies the file and remove the `example-` prefix. If you don't have access to the find command, you can do it manually.

```bash
find . -type f -name 'example-*' -exec bash -c 'cp -rf "$0" "${0/example-/}"' {} \;
```

1. Download the default assets

> The `&& \` is used to combine multiple commands into a single line in a Unix-like command shell. By using && \, the two commands are executed sequentially and only if the first command succeeds. If the first command fails, the second command will not be executed, saving you from potential errors.

```bash
git clone https://git.mc8051.de/nitro/arcturus-morningstar-default-swf-pack.git assets/swf/ && \
git clone https://git.mc8051.de/nitro/default-assets.git assets/assets/ && \
wget -O room.nitro.zip https://git.mc8051.de/attachments/e948e603-d0ea-4948-b313-e8290a1c4bc9 && \
unzip -o room.nitro.zip -d assets/assets/bundled/generic && \
docker compose up db -d
```
⚠ **The database port is exposed to `3010` by default** ⚠


2. Configure the `.env` to your needs

3. Download SQL updates: 
https://git.mc8051.de/nitro/Arcturus-Community/src/branch/ms4/dev/sqlupdates

4. Manually initialize database with HeidiSQL.
- Download `HeidiSQL` from: https://www.heidisql.com/download.php
- Open `HeidiSQL.exe` and connect to the nitro-docker-db container

```text
# **Default login credentials using HeidySQL:**
# Network type: MariaDB or MySQL (TCP/IP)
# Library: libmysql.dll
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

If you set-up a clean database you also wan't to create new permission groups. This is the new permission structure by Arcturus.
- Go to **File** --> **Run SQL file...**  and open **perms_groups.sql** Located at: ./arcturus


5. Update emulator settings with HeidiSQL

- Select `Query` then copy paste the follwing queries:

```sql
-- requirements for the camera mod
UPDATE emulator_settings SET `value`='http://127.0.0.1:8080/usercontent/camera/' WHERE  `key`='camera.url';
UPDATE emulator_settings SET `value`='/app/assets/usercontent/camera/' WHERE  `key`='imager.location.output.camera';
UPDATE emulator_settings SET `value`='/app/assets/usercontent/camera/thumbnail/' WHERE  `key`='imager.location.output.thumbnail';

-- because we have no image.php proxy which is set by default to proxy youtube images we do a microservice aproach by proxy data through a go service
UPDATE emulator_settings SET `value`='http://127.0.0.1:8080/api/imageproxy/0x0/http://img.youtube.com/vi/%video%/default.jpg' WHERE  `key`='imager.url.youtube';

-- This will Disable console mode for Arcturus because we are using docker.
UPDATE emulator_settings SET `value`='0' WHERE `key`='console.mode';

-- badges are dynamically generated by Nitro. This setting is only useful if a) you have group_badge.nitro and swf/c_images/Badgeparts/ in sync b) you wan't to hide the the error message
UPDATE emulator_settings SET `value`='/app/assets/usercontent/badgeparts/generated/' WHERE  `key`='imager.location.output.badges';
UPDATE emulator_settings SET `value`='/app/assets/swf/c_images/Badgeparts' WHERE  `key`='imager.location.badgeparts';

```

- Press `F9` on your keyboard to run the queries

6. Start Asset Server, Build assets locally, Arcturus Community Emulator and Nitro

```bash
docker compose up assets -d && \
docker compose up assets-build --build && \
docker compose up arcturus --build -d
```

7. Update the: `nitro/renderer-config.json` and `nitro/ui-config.json` values to your setup. If the deployment is buggy or throws any errors check the json files for updates. then Build and Start Nitro

```bash
docker compose up nitro --build -d
```

> [habbo-downloader](https://github.com/higoka/habbo-downloader) requires **Node.js 15.0** or higher you can install the newest version with the following command:

```bash
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && \
nvm install --lts
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
mv assets/swf/gordon/*PRODUCTION* assets/swf/gordon/PRODUCTION && \
./assets-build.sh
```


## Update Languages

```bash
habbo-downloader --output ./assets/translation --domain com --command gamedata && \
cd ./assets/translation && \
cp -rf gamedata/external*.txt ../swf/gamedata/ && \
cd ../.. && \
./assets-build.sh && \
cd ./assets/translation && \
python FurnitureDataTranslator.py && \
python SQLGenerator.py && \
python external_text.py --domain com
```

* run SQL file
* maybe run other `./assets/translation/*.sql` files which are fixes for Arcturus catalog like to display Song names/preview, fixing crackables or known wrong item bases.

```bash
docker compose restart arcturus
```

## AtomCMS

1. change [`.cms.env`](/.cms.env) to your needs

2. Check your permissions table. Use [**perms_groups.sql**](/arcturus/perms_groups.sql) if unclear. AtomCMS is not using the new permission layout so we are legacy supporting it by "copy" the most important values.

4. Start the CMS
```bash
docker compose up cms --build -d
```

5. Generate a new secret APP_KEY and update your .cms.env file
```bash
docker compose exec cms php artisan key:generate --show
```

6. Restart the CMS container
```bash
docker compose down cms && docker compose up cms -d
```

7. Seed database
```bash
docker compose exec cms php artisan migrate --seed
```

8. Open the CMS in the browser by default [`127.0.0.1:8081`](http://127.0.0.1:8081/) and do the basic setup.

9. Update automcms settings with HeidiSQL

```sql
UPDATE website_settings SET `value` = 'http://127.0.0.1:8080/api/imager/?figure=' WHERE  `key` = 'avatar_imager';
UPDATE website_settings SET `value` = 'http://127.0.0.1:8080/swf/c_images/album1584' WHERE  `key` = 'badges_path';
UPDATE website_settings SET `value` = 'http://127.0.0.1:8080/usercontent/badgeparts/generated' WHERE  `key` = 'group_badge_path';
UPDATE website_settings SET `value` = 'http://127.0.0.1:8080/swf/dcr/hof_furni' WHERE  `key` = 'furniture_icons_path';
UPDATE website_settings SET `value` = '/housekeeping' WHERE  `key` = 'housekeeping_url';

UPDATE website_settings SET `value` = 'arcturus' WHERE  `key` = 'rcon_ip';
UPDATE website_settings SET `value` = '3001' WHERE  `key` = 'rcon_port';

-- check values - these values are for the perms_groups.sql
UPDATE website_settings SET `value` = '4' WHERE  `key` = 'min_staff_rank';
UPDATE website_settings SET `value` = '5' WHERE  `key` = 'min_maintenance_login_rank';
UPDATE website_settings SET `value` = '6' WHERE  `key` = 'min_housekeeping_rank';

UPDATE website_settings SET `value` = '0' WHERE  `key` = 'cloudflare_turnstile_enabled';
```

**ℹ Notice**: badgeparts generator must be set up in arcturus and all files must be synced with the badge_parts.nitro

## Create an archive/backup

### Export running containers
```bash
bash ./export_containers.sh
```

### Create manual database backup
```bash
docker compose exec backup backup-now
```

### Save all data
```bash
7z a -mx=9 nitro-$(date -d "today" +"%Y%m%d_%H%M").7z ./ '-x!db/data' '-x!.git/' '-x!logs/' '-x!cache/'
```