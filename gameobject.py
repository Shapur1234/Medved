import globals
import pygame
import random


class Vector2D:
    def __init__(self, x, y) -> None:
        self.X = x
        self.Y = y

    def __str__(self):
        return f"X:{self.X}, Y:{self.Y}"

    def ToTuple(self):
        return (self.X, self.Y)


class Texture2D:
    def __init__(self, path, size):
        self.Path = path
        self.Size = size
        self.Image = pygame.transform.scale(pygame.image.load(self.Path), (self.Size.X, self.Size.Y))

    def __str__(self) -> str:
        return f"Path: {self.Path}"

    def ResetImageSize(self) -> None:
        self.Image = pygame.transform.scale(pygame.image.load(self.Path), (self.Size.X, self.Size.Y))

class Level:
    def __init__(self, texturePath):
        self.Texture = Texture2D(texturePath, Vector2D(globals.ScreenWidth, globals.ScreenHeight))
        self.Accesible = True

        self.Spawns = SpawnCollection(5)

    def GetRect(self):
        return (0, 0, globals.ScreenWidth, globals.ScreenHeight)

    def Draw(self, surface) -> None:
      surface.blit(self.Texture.Image, self.GetRect())


class LevelLayout:
    def __init__(self):
        self.Size = Vector2D(2, 2)
        self.Layout = [[Level("Textures/Levels/Les.jpg"), Level("Textures/Levels/Lidl.jpeg")],
                       [Level("Textures/Levels/Poust.jpeg"), Level("Textures/Levels/Sibir.png")]]

    def GetLevel(self, pos):
        try:
            return self.Layout[pos.Y][pos.X]
        except IndexError:
            return self.Layout[0][0]

    def IsFitToMap(self, pos) -> bool:
        return 0 <= pos.X < self.Size.X and 0 <= pos.Y < self.Size.Y


class Spawn:
    def __init__(self, type):
        self.Size = Vector2D(80, 80)
        self.Pos = Vector2D(random.randint(0, globals.ScreenWidth - self.Size.X), random.randint(0, globals.ScreenHeight - self.Size.Y))
        self.Type = type
        
        if type == "Salam":
            self.Texture = Texture2D("Textures/Salam.png", self.Size)
            self.Facing = "Left"
        elif type == "Salam impostor":
            self.Texture = Texture2D("Textures/Salam.png", self.Size)
            self.Facing = "Rigth"

    def ResetPos(self) -> None:
        self.Pos = Vector2D(random.randint(0, globals.ScreenWidth - self.Size.X), random.randint(0, globals.ScreenHeight - self.Size.Y))

    def GetRect(self):
        return pygame.Rect(int(self.Pos.X), int(self.Pos.Y), self.Size.X, self.Size.Y)

    def Draw(self, surface) -> None:
        surface.blit(self.Texture.Image if self.Facing == "Left" else pygame.transform.flip(self.Texture.Image, True, False), self.GetRect())


class SpawnCollection:
    def __init__(self, amount) -> None:
        self.List = [Spawn("Salam" if random.randint(0, 100) < 80 else "Salam impostor") for i in range(amount)]

    def Draw(self, surface) -> None: 
        for item in self.List:
            item.Draw(surface)

    def GetCollidedSpawnIndexes(self, rect: pygame.Rect):
        return list(map(lambda x: self.List.index(x), filter(lambda x: rect.colliderect(x.GetRect()) > 0, self.List)))


class PlayerSprite:
    def __init__(self, size, pos):
        self.Size = size
        self.Pos = pos
        self.Texture = Texture2D("Textures/Characters/Bear.png", self.Size)

    def GetRect(self):
        return pygame.Rect(int(self.Pos.X), int(self.Pos.Y), self.Size.X, self.Size.Y)

    def Draw(self, surface, facing) -> None:
        surface.blit(self.Texture.Image if facing == "Left" else pygame.transform.flip(self.Texture.Image, True, False), self.GetRect())


class Player:
    def __init__(self) -> None:
        self.WorldPos = Vector2D(0, 0)
  
        self.Size = Vector2D(100, 100)
        self.Pos = Vector2D(500, 00)
        self.Facing = "Left"

        self.PlayerSprite = PlayerSprite(self.Size, self.Pos)
        
        self.MaxHealth = 50
        self.Health = 10

    def ClampCoordinates(self, level) -> None:
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

    def MoveSprite(self, amount, level) -> None:
        self.Pos.X += amount.X
        self.Pos.Y += amount.Y
        self.Facing = self.Facing if amount.X == 0 else "Left" if amount.X < 0 else "Right"

        self.ClampCoordinates(level)

    def DrawSprite(self, surface) -> None:
        self.PlayerSprite.Draw(surface, self.Facing)

    def ModHealth(self, amount) -> None:
        self.Health += amount
        if self.Health > self.MaxHealth:
            self.Health = self.MaxHealth
        elif self.Health < 0:
            self.Health = 0
