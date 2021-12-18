import random
import pygame

import globals
import gameobject


def main():
    pygame.init()
    pygame.display.set_caption("🐻 🐻 🐻 Los Medvědos vrací úderos 🐻 🐻 🐻")
    pygame.time.set_timer(pygame.USEREVENT + 1, globals.MovementFrequency)

    screen = pygame.display.set_mode((globals.ScreenWidth, globals.ScreenHeight))

    Play(screen)

def Play(surface) -> None:
    player = gameobject.Player()
    svet = gameobject.LevelLayout()

    someFont = pygame.font.SysFont(None, 16)

    running = True
    while running:
        displayUpdated = False
        inputMovement = PosChangeFromInput()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT + 1:
                if inputMovement != gameobject.Vector2D(0, 0):
                    player.MoveSprite(inputMovement, svet)
                    inputMovement = gameobject.Vector2D(0, 0)
                    displayUpdated = True

        if displayUpdated:
            currentLevel = svet.GetLevel(player.WorldPos)
            
            currentLevel.Draw(surface)
            currentLevel.Spawns.Draw(surface)
            player.DrawSprite(surface)

            # surface.blit(someFont.render(f"WorldPos:  {player.WorldPos}", True, (255, 0 ,0)), (16, 16))
            DrawHealthBar(surface, player.Health, player.MaxHealth)

            pygame.display.flip()
            
            spawnsCollided = currentLevel.Spawns.GetCollidedSpawnIndexes(player.PlayerSprite.GetRect())
            for i in currentLevel.Spawns.List:
                index = currentLevel.Spawns.List.index(i)
                if index in spawnsCollided:
                    if i.Type == "Salam":
                        player.ModHealth(10)
                        currentLevel.Spawns.List.pop(index)
                    elif i.Type == "Salam impostor":
                        player.ModHealth(-10)
                        currentLevel.Spawns.List[index].ResetPos()

def PosChangeFromInput() -> gameobject.Vector2D:
    pressedKeys = pygame.key.get_pressed()
    return gameobject.Vector2D(1 if pressedKeys[pygame.K_RIGHT] else -1 if pressedKeys[pygame.K_LEFT] else 0, 1 if  pressedKeys[pygame.K_DOWN] else -1 if pressedKeys[pygame.K_UP] else 0)

def DrawHealthBar(surface, health, maxHealth):
    health_bar_lenght = globals.ScreenWidth // 8
    health_unit = maxHealth / health_bar_lenght
    health_bar_state = health // health_unit
    
    pygame.draw.rect(surface, globals.ColorRed, pygame.Rect(3, globals.ScreenHeight - 17, health_bar_state, 14))
    pygame.draw.rect(surface, globals.ColorBlack, pygame.Rect(0, globals.ScreenHeight - 20, health_bar_lenght + 6, 20), 3)

main()