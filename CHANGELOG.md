
<h1>Changelog</h1>

## 3.1.0 (2024/05/20)
------------------
- Major update and bugfixes
- Added `getAngles()` and `setAngles()`
- Added `getAnglesRelative()` and `setAnglesRelative()`, with options to take twirls/midspins into account
- `tiles` list is now type-check friendly
- Updated `Settings` class
- Added support for levels that use `pathData`
- Fixed `writeToFile()` no longer working (again)
- Fixed typos in `_getFileString()` and `_getFileDict()`
- Cleaned up some errors in README.md
- Version number is no longer out of sync

## 3.0.3 (2024/03/18)
------------------
- Minor bugfixes
- Fixed `writeToFile()` no longer working
- Replaced `json.dumps()` with faster `json.dump()` in `writeToFile()`
- Known issue: version number is out of sync

## 3.0.1 (2023/12/02)
------------------
- Minor bugfix
- Fixed markdown bug on README and CHANGELOG
- Removed unnessecary files

## 3.0.0 (2023/12/01)
------------------
- Major update
- Completely overhauled file structure to use a class-based system
- Too much to list! Read the docs for more info

## 2.0.3 (2023/09/23)
------------------
- Minor bugfixes
- Fixed `addEvent()` not detecting `addObject` and `addText` events
- Fixed `removeEvents()` not modifying `leveldict`
- Fixed typo in `replaceField()`
- Added logo to README

## 2.0.2 (2023/09/03)
------------------
- Minor bugfix
- Fixed markdown bug on README and CHANGELOG for real this time

## 2.0.1 (2023/09/03)
------------------
- Minor bugfix
- Fixed markdown bug on README and CHANGELOG (hopefully)

## 2.0.0 (2023/09/03)
------------------
- Major update
- Completely overhauled file reading to use dictionaries instead of strings
- Added `getFileDict()`
- Added 3 new utility functions: `searchEvents()`, `removeEvents()` and `replaceField()`
- `getAngles()`, `setAngles()` and all event functions are now deprecated
- Updated documentation
- README and CHANGELOG now uses markdown

## 0.1.1 (2023/07/17)
------------------
- Minor bugfixes
- Fixed encoding incompatibility
- Fixed output string for `moveDecorations()`

## 0.1.0 (2023/06/15)
------------------
- Minor update
- Added dynamic pivot offset, parallax offset, masking and blending fields to `addDecoration()` and `moveDecorations()`
- Added angleOffset to `setSpeed()`

## 0.0.3 (2023/06/14)
------------------
- Minor bugfix: fixed filename `__init__.py`

## 0.0.2 (2023/06/13)
------------------
- Minor bugfix: `'re'` is no longer a dependency

## 0.0.1 (2023/05/28)
------------------
- First Release