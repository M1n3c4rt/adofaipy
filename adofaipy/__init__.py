import re
import json
from collections import UserDict
from typing import Callable
import copy

class InvalidLevelDictException(Exception):
	pass

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

class Settings(UserDict):
	def __init__(self,*arg,**kw):
		super(Settings, self).__init__(*arg, **kw)
		
class LevelDict:

	def __init__(self, filename : str='', encoding="utf-8-sig") -> None:
		
		self.filename = filename
		self.encoding = encoding
		leveldict = self._getFileDict()
		if 'actions' not in leveldict or 'settings' not in leveldict or ('angleData' not in leveldict and 'pathData' not in leveldict):
			raise InvalidLevelDictException('The provided .adofai file is invalid. (check for missing fields)')

		if "angleData" in leveldict:
			__angleData = leveldict["angleData"]
		else:
			__pathchars = { "R": 0, "p": 15, "J": 30, "E": 45, "T": 60, "o": 75, "U": 90, "q": 105, "G": 120, "Q": 135, "H": 150, "W": 165, "L": 180, "x": 195, "N": 210, "Z": 225, "F": 240, "V": 255, "D": 270, "Y": 285, "B": 300, "C": 315, "M": 330, "A": 345, "!": 999}

			__angleData = []
			for i in leveldict["pathData"]:
				__angleData.append(__pathchars[i])
		
		__angleData.append(__angleData[-1] if __angleData[-1] != 999 else (__angleData[-2]+180)%360)
		actions = leveldict["actions"]
		decorations = leveldict["decorations"] if 'decorations' in leveldict else []
		self.nonFloorDecos = [Decoration(j) for j in decorations if "floor" not in j.keys()]
		self.settings = Settings(leveldict["settings"]) if filename != '' else dict()
		self.tiles = [Tile(0)]
		self.tiles.pop()

		for angle in __angleData:
			self.tiles.append(Tile(angle))

		for action in actions:
			self.tiles[action["floor"]].actions.append(Action(action))

		for deco in decorations:
			if "floor" in deco.keys():
				if deco["floor"] >= len(self.tiles):
					self.tiles[-1].decorations.append(Decoration(deco))
				else:
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

		if self.filename == '':
			return {
				"angleData": [0],
				"settings": dict(),
				"actions" : [],
				"decorations" : []
			}

		a = self._getFileString()
		sp=re.split(r"(?<!\\)(?:\\\\)*(\")",a)

		for i in range(len(sp)):
			if i % 4 == 0:
				sp[i] = re.sub(r"(\n|\t)", "", sp[i])
				sp[i] = re.sub(r"\,(( *)(\]|\}))", "\\3", sp[i])
				sp[i] = re.sub(r"(\]|\})(\[|\{)", "\\1,\\2", sp[i])
			elif i % 2 == 0:
				sp[i] = re.sub(r"(\n)", "\\\\n", sp[i])
				sp[i] = re.sub(r"(\t)", "\\\\t", sp[i])
				sp[i] = re.sub(r"(\r)", "\\\\r", sp[i]) # this is for all zero people who put return carriage characters in their files
		
		a = ''.join(sp)
		final = json.loads(a)
		return final

	def __addTile(self, angle : float, index=None) -> None:
		if index is not None:
			self.tiles.insert(index, Tile(angle))
		else:
			self.tiles.append(Tile(angle))
			self.tiles[-2].angle = angle

	def __addTiles(self, angles : list[float], index=None) -> None:
		
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

	def appendTiles(self, angles : list[float]) -> None:
		"""Adds a list of tiles to the end of the level.
		"""
		self.__addTiles(angles)

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

	def getAnglesRelative(self, ignoretwirls: bool=False, padmidspins: bool=False) -> list[float]:
		"""Gets a list of relative angles (degrees between each pair of tiles.)
		Twirls are taken into account by default. To disable this, set ignoretwirls to True.
		If padmidspins is set to True, midspin values (999) are replaced with 0 instead of being removed in order to keep the list the same length.
		Midspins are always taken into account.
		"""
		absangles = self.getAngles().copy()

		if not ignoretwirls:
			twirls = [event['floor'] for event in self.getActions(lambda x: x['eventType'] == 'Twirl')]
			for twirl in reversed(twirls):
				absangles[twirl:] = [(2*absangles[twirl-1]-angle)%360 if angle != 999 else 999 for angle in absangles[twirl:]]

		midspins = [idx for idx,angle in enumerate(absangles) if angle == 999]
		for midspin in reversed(midspins):
			absangles[midspin+1:] = [(angle+180)%360 if angle != 999 else 999 for angle in absangles[midspin+1:]]

		if not padmidspins:
			absangles = [angle for angle in absangles if angle != 999]

		angles = []
		for idx,angle in enumerate(absangles):
			if angle == 999:
				angles.append(0)
			else:
				if idx == 0:
					angles.append((0-angle+180-1)%360+1)
				else:
					if absangles[idx-1] == 999:
						angles.append((absangles[idx-2]-angle+180-1)%360+1)
					else:
						angles.append((absangles[idx-1]-angle+180-1)%360+1)

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

	def getActions(self, condition : Callable=lambda x: True) -> list[Action]:
		"""Returns a list of actions in the level that meet the given condition.
		Returns a list of all actions if condition is not specified.
		"""
		matches = []
		for tile in self.tiles:
			matches.extend(list(filter(condition, tile.actions)))
				
		return matches
	
	def getDecorations(self, condition : Callable=lambda x: True) -> list[Decoration]:
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

		return self.tiles[tile].pop(index)

	def popDecoration(self, tile, index) -> Decoration:
		"""Removes the decoration at the specified tile at the specified index.
		Returns the event.
		"""

		return self.tiles[tile].pop(index)

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
		final["settings"] = dict(self.settings)
		for tile in self.tiles:
			final["angleData"].append(tile.angle)
			final["actions"].extend([dict(action) for action in tile.actions])
			final["decorations"].extend([dict(decoration) for decoration in tile.decorations])
		
		final["decorations"] += [dict(decoration) for decoration in self.nonFloorDecos]
		final["angleData"].pop()

		name = self.filename if filename is None else filename
		with open(name, "w", encoding=self.encoding) as f:
			json.dump(final, f, indent=4)

def mergelevels(base: LevelDict, new: LevelDict, overwrite:bool=False, exclude_tile_events:bool=False):
	"""Adds all the events from the new level to the base level in-place.
	Angle-based events retain global angle offset but NOT floor number (all angle-based events are on tile 0).
	Tile-based events retain floor number. These events are taken from base if exclude_tile_events is True and from new otherwise.
	Overwrites the events from the base level if overwrite is True.
	"""

	if overwrite:
		for tile in base.tiles:
			if exclude_tile_events:
				tile.actions = [action for action in tile.actions if 'angleOffset' in action]
			else:
				tile.decorations = []
				tile.actions = []

		base.nonFloorDecos = []

	if not exclude_tile_events:
		base.nonFloorDecos.extend(copy.deepcopy(new.nonFloorDecos))

	cumulative_angle = 0
	for tile, angle in zip(new.tiles, new.getAnglesRelative(padmidspins=True)):
		for event in tile.actions:
			if 'angleOffset' in event:
				new_event = copy.deepcopy(event)
				new_event['floor'] = 0
				new_event['angleOffset'] += cumulative_angle
				base.addAction(new_event)
			elif not exclude_tile_events:
				base.addAction(copy.deepcopy(event))

		if not exclude_tile_events:
			for deco in tile.decorations:
				base.addDecoration(copy.deepcopy(deco))

		cumulative_angle += angle