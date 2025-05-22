# FOLIO Offline Shelf Reading

**IN DEVELOPMENT**

A shelf-reading (inventory check) process for FOLIO items.  Using a laptop, a barcode scanner, and a cart.

## Design Goals

- Read one section at at time, with up-to-date inventory data (no advance loading).
- Do the actual shelf-reading quickly, without looking at the laptop screen, unless/until something goes wrong.
- Fix minor shelf order problems quickly, while recording bigger problems for later.
- Quickly record condition issues with no typing.
- Work without network traffic while in the stacks, so good Wi-Fi doesn't matter.
- Store (almost) all data in FOLIO to maintain a single source-of-truth.

## Dependencies

- FOLIO
- MetaDB
- Python

## Development/Deployment

1. Create and configure `config.properties` based on [the example](./config/config.properties.example)
    - This includes creating FOLIO statistical codes and item note types as specified in the example file. 
1. Clone this repo
1. Start docker
```
git clone https://github.com/lehigh-university-libraries/folio-offline-shelf-reading
cd folio-offline-shelf-reading
# cp config/config.properties.example config/config.properties
# make edits to config/config.properties
docker run \
  -v ./:/app
  -p 8080:8080 \
  --rm \
  --name folio-offline-shelf-reading \
  ghcr.io/lehigh-university-libraries/folio-offline-shelf-reading:main
```

## Custom Shelving Order

In some cases, an item's FOLIO-generated shelving order field may not be sufficient to sort items correctly.  See for example [a constraint on Dewey cutter numbers](https://github.com/lehigh-university-libraries/folio-shelving-order?tab=readme-ov-file#non-standard-behavior).

If an item has a note of type `Shelving order`, the value in that field is interpreted as a local shelving order, and is used as a sorting value instead of the item's shelving order field.  The sort logic looks to both fields, so only those items that require a custom local shelving order field need that note defined.

The [FOLIO Update Local Shelving Order](https://github.com/lehigh-university-libraries/folio-update-local-shelving-order) tool adds these items notes to the relevant items, using [FOLIO Shelving Order](https://github.com/lehigh-university-libraries/folio-shelving-order) to generate the local shelving order.

## Attribution

- [Scanning beep sound effect](https://pixabay.com/sound-effects/beep-313342/) by [Musheran](https://pixabay.com/users/musheran-40634446/)
- [Error sound effect](https://pixabay.com/sound-effects/message-notification-103496/) by [freesound_community](https://pixabay.com/users/freesound_community-46691455/)
