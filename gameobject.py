import globals

from typing import Dict, List
import pygame
import random
import time
import os

#----------------------------------------------------------------------------------------------------


class Vector2D:
    def __init__(self, x: float, y: float) -> None:
        self.X = x
        self.Y = y

    def __str__(self) -> str:
        return f"X:{self.X}, Y:{self.Y}"
    
    
    # def __eq__(self, __o: object) -> bool:
    #     if isinstance(__o, Vector2D):
    #         return self.X == __o.X and self.Y == __o.Y
        
    #  return False

    def ToTuple(self) -> tuple:
        return (self.X, self.Y)
    
    X: float
    Y: float


textureCache: Dict = {}
for i in [os.path.relpath(os.path.join(dirpath, file), "Textures") for (dirpath, dirnames, filenames) in os.walk("Textures") for file in filenames]:
    textureCache[i] = pygame.image.load("Textures/" + i)
    
class Texture2D:
    def __init__(self, path: str, size: Vector2D):
        self.Path = path
        self.Size = size
        self.ImageRaw = textureCache[self.Path]
        self.Image = pygame.transform.scale(self.ImageRaw, (self.Size.X, self.Size.Y))

    def __str__(self) -> str:
        return f"Path: {self.Path}"
    
    Path: str
    Size: Vector2D
    ImageRaw: pygame.image
    Image: pygame.image


#----------------------------------------------------------------------------------------------------


class Level:
    def __init__(self, backgroundTexturePath: str):
        self.Texture = Texture2D(backgroundTexturePath, Vector2D(globals.ScreenWidth, globals.ScreenHeight))
        self.Accessible = True

        self.Spawns = SpawnCollection(5)

    def GetRect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, globals.ScreenWidth, globals.ScreenHeight)

    def Draw(self, surface) -> None:
        surface.blit(self.Texture.Image, self.GetRect())

    Texture: Texture2D
    Accessible: bool

class LevelLayout:
    def __init__(self):
        self.Size = Vector2D(3, 3)
        self.Layout = [[Level("Levels/Les.jpg"), Level("Levels/Lidl.jpeg"), Level("Levels/Sibir.png")],
                       [Level("Levels/Poust.jpeg"), Level("Levels/Les.jpg"), Level("Levels/Lidl.jpeg")],
                       [Level("Levels/Les.jpg"), Level("Levels/Lidl.jpeg"), Level("Levels/Sibir.png")]]
        

    def GetLevel(self, pos: Vector2D) -> List[List[Level]]:
        try:
            return self.Layout[pos.Y][pos.X]
        except IndexError:
            return self.Layout[0][0]

    def IsFitToMap(self, pos: Vector2D) -> bool:
        return 0 <= pos.X < self.Size.X and 0 <= pos.Y < self.Size.Y
    
    def RemoveExpiredSpawns(self) -> None:
        for item in [j for sub in self.Layout for j in sub]:
            item.Spawns.RemoveExpiredSpawns()
            
    Size: Vector2D
    Layout: List[List[Level]]


class SpawnCollection:
    def __init__(self, amount: int) -> None:
        self.List = [Spawn("Salam" if random.randint(0, 100) < 80 else "Mine") for i in range(amount)]

    def Draw(self, surface) -> None: 
        for item in self.List:
            item.Draw(surface)

    def GetCollidedSpawnIndexes(self, rect: pygame.Rect) -> map:
        return map(lambda x: self.List.index(x), filter(lambda x: rect.colliderect(x.GetRect()) > 0, self.List))

    def RemoveExpiredSpawns(self) -> None:
        self.List = list(filter(lambda x: True if x.LifeTime < 0 else (time.time() - x.SpawnTime) < x.LifeTime, self.List))
        
    List: List


#----------------------------------------------------------------------------------------------------


class BaseSprite:
    def GetRect(self) -> pygame.Rect:
        return pygame.Rect(int(self.Pos.X), int(self.Pos.Y), int(self.Size.X), int(self.Size.Y))

    def Draw(self, surface: pygame.surface) -> None:
        surface.blit(self.Texture.Image if self.Facing == "Left" else pygame.transform.flip(self.Texture.Image, True, False), self.GetRect())
        
    Pos: Vector2D
    Size: Vector2D
    Facing: str
    Texture: Texture2D
        

class Spawn(BaseSprite):
    def __init__(self, type: str, pos: Vector2D = None):
        self.Type = type
        self.SpawnTime = time.time()
        self.LifeTime = -1
        self.Facing = "Left"
        
        if self.Type == "Salam":
            self.Size = Vector2D(80, 80)
            self.Texture = Texture2D("Salam.png", self.Size)
        elif self.Type == "Mine":
            self.Size = Vector2D(60, 60)
            self.Texture = Texture2D("Mine.png", self.Size)
        elif self.Type == "Explosion":
            self.Size = Vector2D(60, 60)
            self.Texture = Texture2D("Explosion.jpeg", self.Size)
            self.LifeTime = 1
        
        self.Pos = Vector2D(random.randint(0, globals.ScreenWidth - self.Size.X), random.randint(0, globals.ScreenHeight - self.Size.Y)) if not pos else pos 
            
    def ResetPos(self, playerRect: pygame.Rect) -> None:
        while True:
            self.Pos = Vector2D(random.randint(0, globals.ScreenWidth - self.Size.X), random.randint(0, globals.ScreenHeight - self.Size.Y))
            if not self.GetRect().colliderect(playerRect):
                break
            
        Type: str
        SpawnTime: float
        LifeTime: float


class Player(BaseSprite):
    def __init__(self) -> None:
        self.WorldPos = Vector2D(0, 0)
  
        self.Size = Vector2D(100, 100)
        self.Pos = Vector2D(500, 00)
        self.Facing = "Left"
        self.Texture = Texture2D("Bear.png", self.Size)

        self.MaxHealth = 50
        self.Health = 40

    def ClampCoordinates(self, level: Level) -> None:
        if (self.Pos.X < 0):
            if level.IsFitToMap(Vector2D(self.WorldPos.X - 1, self.WorldPos.Y)):
                self.WorldPos.X -= 1
                self.Pos.X = globals.ScreenWidth - self.Size.X
            else:
                self.Pos.X = 0

        elif (self.Pos.X + self.Size.X > globals.ScreenWidth):
            if level.IsFitToMap(Vector2D(self.WorldPos.X + 1, self.WorldPos.Y)):
                self.WorldPos.X += 1
                self.Pos.X = 0
            else:
              self.Pos.X = globals.ScreenWidth - self.Size.X

        if (self.Pos.Y < 0):
            if level.IsFitToMap(Vector2D(self.WorldPos.X, self.WorldPos.Y - 1)):
                self.WorldPos.Y -= 1
                self.Pos.Y = globals.ScreenHeight - self.Size.Y
            else:
                self.Pos.Y = 0

        elif (self.Pos.Y + self.Size.Y > globals.ScreenHeight):
            if level.IsFitToMap(Vector2D(self.WorldPos.X, self.WorldPos.Y + 1)):
                self.WorldPos.Y += 1
                self.Pos.Y = 0
            else:
              self.Pos.Y = globals.ScreenHeight - self.Size.Y

    def Move(self, amount: Vector2D, level: Level) -> None:
        self.Pos.X += amount.X
        self.Pos.Y += amount.Y
        self.Facing = self.Facing if amount.X == 0 else "Left" if amount.X < 0 else "Right"

        self.ClampCoordinates(level)

    def ModHealth(self, amount: int) -> None:
        self.Health += amount
        if self.Health > self.MaxHealth:
            self.Health = self.MaxHealth
        elif self.Health < 0:
            self.Health = 0
            
    WorldPos: Vector2D
    
    MaxHealth: float
    Health: float


#----------------------------------------------------------------------------------------------------


class GUI:
    def __init__(self, scale: float = 1) -> None:
        self.Scale = scale
        
        self.HealthBarSize = None
        self.HealthBarPos = None
        self.CalcUIDimensions()

    def CalcUIDimensions(self) -> None:
        self.HealthBarSize = Vector2D(int((globals.ScreenWidth / 6) * self.Scale), int((globals.ScreenHeight / 16) * self.Scale))
        self.HealthBarPos = Vector2D(int(globals.ScreenWidth * 0.01), globals.ScreenHeight - self.HealthBarSize.Y - int(globals.ScreenWidth * 0.01))

    def DrawHealthBar(self, surface, currentHealth: int, maxHealth: int) -> None:
        pygame.draw.rect(surface, globals.ColorWhite, pygame.Rect(self.HealthBarPos.X, self.HealthBarPos.Y, self.HealthBarSize.X, self.HealthBarSize.Y))
        pygame.draw.rect(surface, globals.ColorRed, pygame.Rect(self.HealthBarPos.X, self.HealthBarPos.Y, int(self.HealthBarSize.X * (currentHealth / maxHealth)), self.HealthBarSize.Y))
        pygame.draw.rect(surface, globals.ColorBlack, pygame.Rect(self.HealthBarPos.X, self.HealthBarPos.Y, self.HealthBarSize.X, self.HealthBarSize.Y), int(globals.ScreenWidth * 0.005))
        
    Scale: float
    
    HealthBarSize: float
    HealthBarPos: float