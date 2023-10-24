# Nitro Imager

This tool serves as a server-side habbo-imager using the same avatar generator from nitro-renderer. It will download & cache in memory `.nitro` assets. Rendered figures will also save to a local folder to prevent re-renders. You will use the same process as your nitro-client to update assets for the imager.

## URL paramaters

Their are a few different options you may pass as URL parameters to generate figures with different actions. All parameters are optional.

| key            | default | description                                                         |
| -------------- | ------- | ------------------------------------------------------------------- |
| figure         | null    | The figure string to be rendered                                    |
| action         | null    | The actions to render, see actions below                            |
| gesture        | std     | The gesture to render, see gestures below                           |
| direction      | 2       | The direction to render, from 0-7                                   |
| head_direction | 2       | The head direction to render, from 0-7                              |
| headonly       | 0       | A value of `0` or `1`                                               |
| dance          | 0       | A dance id of 0-4 to render                                         |
| effect         | 0       | An effect id to render                                              |
| size           | n       | The size to render, see sizes below                                 |
| frame_num      | 0       | The frame number to render                                          |
| img_format     | png     | A value of `png` or `gif`. Gif will render all frames of the figure |

## Actions

You may render multiple actions with a comma separater

Example: `&action=wlk,wav,drk=1`

##### Posture

| key    | description                  |
| ------ | ---------------------------- |
| std    | Renders the standing posture |
| wlk,mv | Renders the walking posture  |
| sit    | Renders the sitting posture  |
| lay    | Renders the laying posture   |

##### Expression

| key      | description                     |
| -------- | ------------------------------- |
| wav,wave | Renders the waving expression   |
| blow     | Renders the kissing expression  |
| laugh    | Renders the laughing expression |
| respect  | Renders the respect expression  |

##### Carry / Drink

To hold a certain drink, use an equal separator with the hand item id. You can only render one of these options at a time

| key      | description              |
| -------- | ------------------------ |
| crr,cri  | Renders the carry action |
| drk,usei | Renders the drink action |

## Gestures

| key | description                    |
| --- | ------------------------------ |
| std | Renders the standard gesture   |
| agr | Renders the aggravated gesture |
| sad | Renders the sad gesture        |
| sml | Renders the smile gesture      |
| srp | Renders the surprised gesture  |

## Sizes

| key | description                  |
| --- | ---------------------------- |
| s   | Renders the small size (0.5) |
| n   | Renders the normal size (1)  |
| l   | Renders the large size (2)   |

## Known Issues

-   GIFs are only able to render 1 bit alpha channels, therefore most effects will not correctly render due to using many different alpha values.
-   The rendered canvas size may not match habbos imager exactly, we will hopefully have this addressed soon.

## Test String:
[`figure=hd-180-1.ch-255-66.lg-280-110.sh-305-62.ha-1012-110.hr-828-61&action=std,wav&gesture=std&direction=2&head_direction=2&size=l&img_format=png`](http://labs.habox.org/generator-avatar)