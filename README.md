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
