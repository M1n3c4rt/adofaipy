import re
import json
from collections import UserDict
from typing import Callable

class Action(UserDict):
	def __init__(self,*arg,**kw):
		super(Action, self).__init__(*arg, **kw)

class Decoration(UserDict):
	def __init__(self,*arg,**kw):
		super(Decoration, self).__init__(*arg, **kw)

class Tile():
	def __init__(self, angle : float, actions : list[Action]=[], decorations : list[Decoration]=[]):
		self.angle = angle
		self.actions = actions.copy()
		self.decorations = decorations.copy()

class Settings():
	def __init__(self, values : dict) -> None:
		self.version = values["version"]
		self.artist = values["artist"]
		self.specialArtistType = values["specialArtistType"]
		self.artistPermission = values["artistPermission"]
		self.song = values["song"]
		self.author = values["author"]
		self.separateCountdownTime = values["separateCountdownTime"]
		self.previewImage = values["previewImage"]
		self.previewIcon = values["previewIcon"]
		self.previewIconColor = values["previewIconColor"]
		self.previewSongStart = values["previewSongStart"]
		self.previewSongDuration = values["previewSongDuration"]
		self.seizureWarning = values["seizureWarning"]
		self.levelDesc = values["levelDesc"]
		self.levelTags = values["levelTags"]
		self.artistLinks = values["artistLinks"]
		self.speedTrialAim = values["speedTrialAim"]
		self.difficulty = values["difficulty"]
		self.requiredMods = values["requiredMods"]
		self.songFilename = values["songFilename"]
		self.bpm = values["bpm"]
		self.volume = values["volume"]
		self.offset = values["offset"]
		self.pitch = values["pitch"]
		self.hitsound = values["hitsound"]
		self.hitsoundVolume = values["hitsoundVolume"]
		self.countdownTicks = values["countdownTicks"]
		self.trackColorType = values["trackColorType"]
		self.trackColor = values["trackColor"]
		self.secondaryTrackColor = values["secondaryTrackColor"]
		self.trackColorAnimDuration = values["trackColorAnimDuration"]
		self.trackColorPulse = values["trackColorPulse"]
		self.trackPulseLength = values["trackPulseLength"]
		self.trackStyle = values["trackStyle"]
		self.trackTexture = values["trackTexture"]
		self.trackTextureScale = values["trackTextureScale"]
		self.trackGlowIntensity = values["trackGlowIntensity"]
		self.trackAnimation = values["trackAnimation"]
		self.beatsAhead = values["beatsAhead"]
		self.trackDisappearAnimation = values["trackDisappearAnimation"]
		self.beatsBehind = values["beatsBehind"]
		self.backgroundColor = values["backgroundColor"]
		self.showDefaultBGIfNoImage = values["showDefaultBGIfNoImage"]
		self.showDefaultBGTile = values["showDefaultBGTile"]
		self.defaultBGTileColor = values["defaultBGTileColor"]
		self.defaultBGShapeType = values["defaultBGShapeType"]
		self.defaultBGShapeColor = values["defaultBGShapeColor"]
		self.bgImage = values["bgImage"]
		self.bgImageColor = values["bgImageColor"]
		self.parallax = values["parallax"]
		self.bgDisplayMode = values["bgDisplayMode"]
		self.imageSmoothing = values["imageSmoothing"]
		self.lockRot = values["lockRot"]
		self.loopBG = values["loopBG"]
		self.scalingRatio = values["scalingRatio"]
		self.relativeTo = values["relativeTo"]
		self.position = values["position"]
		self.rotation = values["rotation"]
		self.zoom = values["zoom"]
		self.pulseOnFloor = values["pulseOnFloor"]
		self.bgVideo = values["bgVideo"]
		self.loopVideo = values["loopVideo"]
		self.vidOffset = values["vidOffset"]
		self.floorIconOutlines = values["floorIconOutlines"]
		self.stickToFloors = values["stickToFloors"]
		self.planetEase = values["planetEase"]
		self.planetEaseParts = values["planetEaseParts"]
		self.planetEasePartBehavior = values["planetEasePartBehavior"]
		self.defaultTextColor = values["defaultTextColor"]
		self.defaultTextShadowColor = values["defaultTextShadowColor"]
		self.congratsText = values["congratsText"]
		self.perfectText = values["perfectText"]
		self.legacyFlash = values["legacyFlash"]
		self.legacyCamRelativeTo = values["legacyCamRelativeTo"]
		self.legacySpriteTiles = values["legacySpriteTiles"]
		
class LevelDict:

	def __init__(self, filename : str, encoding="utf-8-sig") -> None:
		
		self.filename = filename
		self.encoding = encoding
		leveldict = self._getFileDict()

		if "angleData" in leveldict:
			__angleData = leveldict["angleData"]
		else:
			__pathchars = { "R": 0, "p": 15, "J": 30, "E": 45, "T": 60, "o": 75, "U": 90, "q": 105, "G": 120, "Q": 135, "H": 150, "W": 165, "L": 180, "x": 195, "N": 210, "Z": 225, "F": 240, "V": 255, "D": 270, "Y": 285, "B": 300, "C": 315, "M": 330, "A": 345, "!": 999}

			__angleData = []
			for i in "".split(leveldict["pathData"]):
				__angleData.append(__pathchars[i])
		
		__angleData.append(__angleData[-1] if __angleData[-1] != 999 else (__angleData[-2]+180)%360)
		actions = leveldict["actions"]
		decorations = leveldict["decorations"]
		self.nonFloorDecos = [Decoration(j) for j in decorations if "floor" not in j.keys()]
		self.settings = Settings(leveldict["settings"])
		self.tiles = [Tile(0)]
		self.tiles.pop()

		for angle in __angleData:
			self.tiles.append(Tile(angle))

		for action in actions:
			self.tiles[action["floor"]].actions.append(Action(action))

		for deco in decorations:
			if "floor" in deco.keys():
				self.tiles[deco["floor"]].decorations.append(Decoration(deco))

	def _getFileString(self) -> str:
		"""Returns the specified file in string format.
		It is recommended to use getFileDict() unless absolutely necessary.
		"""
		with open(self.filename, "r", encoding=self.encoding) as f:
			s = f.read()
			return s

	def _getFileDict(self) -> dict:
		"""Returns the specified file in the form of nested dictionaries and lists.
		"""
		a = self._getFileString()
		sp=re.split(r"(?<!\\)(?:\\\\)*(\")",a)

		for i in range(len(sp)):
			if i % 4 == 0:
				sp[i] = re.sub(r"(\n|\t)", "", sp[i])
				sp[i] = re.sub(r"\,(( *)(\]|\}))", "\\3", sp[i])
				sp[i] = re.sub(r"(\]|\})(\[|\{)", "\\1,\\2", sp[i])
		
		a = ''.join(sp)
		final = json.loads(a)
		return final

	def __addTile(self, angle : float, index : int=None) -> None:
		if index is not None:
			self.tiles.insert(index, Tile(angle))
		else:
			self.tiles.insert(len(self.tiles)-1, Tile(angle))
			self.tiles[len(self.tiles)-1].angle = self.tiles[len(self.tiles)-2].angle

	def __addTiles(self, angles : list[float], index : int=None) -> None:
		
		if index is not None:
			for angle in reversed(angles):
				self.__addTile(angle, index)
		else:
			for angle in angles:
				self.__addTile(angle)

	def appendTile(self, angle : float) -> None:
		"""Adds a single tile to the end of the level.
		"""
		self.__addTile(angle)
		for i in range(len(self.tiles)-1, len(self.tiles)):
			for action in self.tiles[i].actions:
				action["floor"] += 1
			for deco in self.tiles[i].decorations:
				deco["floor"] += 1

	def appendTiles(self, angles : list[float]) -> None:
		"""Adds a list of tiles to the end of the level.
		"""
		self.__addTiles(angles)
		for i in range(len(self.tiles)-1, len(self.tiles)):
			for action in self.tiles[i].actions:
				action["floor"] += len(angles)
			for deco in self.tiles[i].decorations:
				deco["floor"] += len(angles)

	def insertTile(self, angle : float, index : int) -> None:
		"""Adds a single tile to the level before the specified index.
		"""
		self.__addTile(angle, index)
		for i in range(index+1, len(self.tiles)):
			for action in self.tiles[i].actions:
				action["floor"] += 1
			for deco in self.tiles[i].decorations:
				deco["floor"] += 1

	def insertTiles(self, angles : list[float], index : int) -> None:
		"""Adds a list of tiles to the level before the specified index.
		"""
		self.__addTiles(angles, index)
		for i in range(index+len(angles), len(self.tiles)):
			for action in self.tiles[i].actions:
				action["floor"] += len(angles)
			for deco in self.tiles[i].decorations:
				deco["floor"] += len(angles)

	def getAngles(self) -> list[float]:
		"""Returns a list of angles for each tile.
		"""
		angles = []
		for tile in self.tiles:
			angles.append(tile.angle)
		return angles
	
	def setAngles(self, angles: list[float]) -> None:
		"""Writes a list of angles to angleData.
		The list is truncated if it's too big, and the track is truncated if the list is too small.
		"""
		self.tiles = self.tiles[:len(angles)]
		for tile,angle in zip(self.tiles,angles):
			tile.angle = angle

	def getAnglesRelative(self, ignoretwirls: bool=False) -> list[float]:
		"""Gets a list of relative angles (degrees between each pair of tiles.)
		Twirls are taken into account by default. To disable this, set ignoretwirls to True.
		Midspins are always taken into account.
		"""
		absangles = self.getAngles()
		midspins = []
		anglesrev = list(reversed(absangles)).copy()
		for idx,angle in enumerate(anglesrev):
			if angle == 999:
				for idx_ in range(idx):
					anglesrev[idx_] = (anglesrev[idx_] + 180) % 360
				print(anglesrev.pop(idx))
		absangles = list(reversed(anglesrev))

		angles = []
		for angle,angle_ in zip(absangles,absangles[1:]):
			angles.append(angle - angle_ + 180)

		angles.insert(0,180)

		twirls = [event['floor'] for event in self.getActions(lambda x: x['eventType'] == 'Twirl')]
		twirltiles = []

		if len(twirls)%2 == 1:
			twirls.append(len(self.tiles)+10)

		for i in range(0,len(twirls),2):
			twirltiles += list(range(twirls[i],twirls[i+1]))

		offset = 0
		if not ignoretwirls:
			for idx,angle in enumerate(angles):
				if idx in midspins:
					offset += 1
				if idx+offset in twirltiles:
					angles[idx] = (((360-angle)-1)%360)+1 if angle != 999 else 999

		angles = [(angle-1)%360 + 1 for angle in angles]

		return angles
	
	def setAnglesRelative(self, angles: list[float]) -> None:
		"""Sets a list of relative angles (degrees between pairs of tiles).
		"""
		nangles = [0]
		for angle in angles:
			nangles.append((nangles[-1] - angle + 180)%360)

		nangles.pop(0)
		self.setAngles(nangles)

	def addAction(self, event : Action) -> int:
		"""Adds the given action to the level.
		Returns the index of the event within the tile.
		"""

		self.tiles[event["floor"]].actions.append(event)
		return len(self.tiles[event["floor"]].actions) - 1

	def addDecoration(self, event : Decoration) -> int:
		"""Adds the given decoration to the level.
		Returns the index of the event within the tile / within the list of non-floor decorations.
		"""
		
		if "floor" in event.keys():
			self.tiles[event["floor"]].decorations.append(event)
			return len(self.tiles[event["floor"]].decorations) - 1
		else:
			self.nonFloorDecos.append(event)
			return len(self.nonFloorDecos) - 1

	def getActions(self, condition : Callable) -> list[Action]:
		"""Returns a list of actions in the level that meet the given condition.
		Returns a list of all actions if condition is not specified.
		"""
		matches = []
		for tile in self.tiles:
			matches.extend(list(filter(condition, tile.actions)))
				
		return matches
	
	def getDecorations(self, condition : Callable) -> list[Decoration]:
		"""Returns a list of decorations in the level that meet the given condition.
		Returns a list of all decorations if condition is not specified.
		"""
		matches = []
		for tile in self.tiles:
			matches.extend(list(filter(condition, tile.decorations)))
		matches.extend(list(filter(condition, self.nonFloorDecos)))
		return matches

	def removeActions(self, condition : Callable) -> list[Action]:
		"""Removes all actions in the level that meet the given condition.
		Returns a list of removed actions.
		"""
		matches = []
		for tile in self.tiles:
			matches.extend(list(filter(condition, tile.actions)))
		
		for tile in self.tiles:
			tile.actions = [action for action in tile.actions if action not in matches]

		return matches
	
	def removeDecorations(self, condition : Callable) -> list[Decoration]:
		"""Removes all decorations in the level that meet the given condition.
		Returns a list of removed decorations.
		"""
		matches = []
		for tile in self.tiles:
			matches.extend(list(filter(condition, tile.decorations)))
		matches.extend(list(filter(condition, self.nonFloorDecos)))

		for tile in self.tiles:
			tile.decorations = [deco for deco in tile.decorations if deco not in matches]
		self.nonFloorDecos = [deco for deco in self.nonFloorDecos if deco not in matches]

		return matches

	def popAction(self, tile : int, index : int) -> Action:
		"""Removes the action at the specified tile at the specified index.
		Returns the event.
		"""

		return self.tiles[tile].actions[index].pop()

	def popDecoration(self, tile, index) -> Decoration:
		"""Removes the decoration at the specified tile at the specified index.
		Returns the event.
		"""

		return self.tiles[tile].decorations[index].pop()

	def replaceFieldAction(self, condition : Callable, field : str, new) -> None:
		"""Changes the value of "field" to "new" in all actions that meet the given condition.
		"""
		eventlist = self.removeActions(condition)
		for action in eventlist:
			if field in action:
				action[field] = new

		for action in eventlist:
			self.addAction(action)

	def replaceFieldDecoration(self, condition : Callable, field : str, new) -> None:
		"""Changes the value of "field" to "new" in all decorations that meet the given condition.
		"""
		eventlist = self.removeDecorations(condition)
		for deco in eventlist:
			if field in deco:
				deco[field] = new

		for deco in eventlist:
			self.addDecoration(deco)

	def _writeDictToFile(self, leveldict : dict, filename : str=None):
		"""Writes the given dictionary to the specified file.
		Overwrites the original file if filename is not specified.
		"""
		name = self.filename if filename is None else filename
		with open(name, "w", encoding=self.encoding) as f:
			json.dump(leveldict, f, indent=4)

	def writeToFile(self, filename : str=None) -> None:
		"""Writes the level to the specified file.
		Overwrites the original file if filename is not specified.
		"""
		
		final = {"angleData": [], "settings": {}, "actions": [], "decorations": []}
		final["settings"] = vars(self.settings)
		for tile in self.tiles:
			final["angleData"].append(tile.angle)
			final["actions"].extend([dict(action) for action in tile.actions])
			final["decorations"].extend([dict(decoration) for decoration in tile.decorations])
		
		final["decorations"] += [dict(decoration) for decoration in self.nonFloorDecos]
		final["angleData"].pop()

		name = self.filename if filename is None else filename
		with open(name, "w", encoding=self.encoding) as f:
			json.dump(final, f, indent=4)
